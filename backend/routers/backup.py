# backend/routers/backup.py

import os
import re
import subprocess
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .auth import get_current_user, get_pool
from database import rows_to_dicts

router = APIRouter()

# Directory where server-side dump files are stored
BACKUP_DIR = Path("backups")

# Parse DATABASE_URL to extract connection components for psql/pg_dump
_RAW_DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pos_user:pos_password@localhost:5432/pos_db",
)

def _parse_db_url(url: str):
    """Extract host, port, user, password, dbname from a postgres:// URL."""
    m = re.match(
        r"postgresql://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/(.+)", url
    )
    if not m:
        return {}
    return {
        "user": m.group(1),
        "password": m.group(2),
        "host": m.group(3),
        "port": m.group(4) or "5432",
        "dbname": m.group(5),
    }

_DB = _parse_db_url(_RAW_DB_URL)


def _psql_env():
    """Return env dict with PGPASSWORD set for psql/pg_dump subprocess calls."""
    env = os.environ.copy()
    if _DB.get("password"):
        env["PGPASSWORD"] = _DB["password"]
    return env


def _psql_base_args():
    """Return psql command + connection flags for the default database."""
    return [
        "psql",
        "-h", _DB.get("host", "localhost"),
        "-p", _DB.get("port", "5432"),
        "-U", _DB.get("user", "pos_user"),
        "-d", _DB.get("dbname", "pos_db"),
    ]


def _psql_admin_args(dbname: str):
    """Return psql command + connection flags for a specific database."""
    return [
        "psql",
        "-h", _DB.get("host", "localhost"),
        "-p", _DB.get("port", "5432"),
        "-U", _DB.get("user", "pos_user"),
        "-d", dbname,
    ]


# ── History CRUD ──────────────────────────────────────────────

class BackupCreate(BaseModel):
    backup_date: str
    file_name: str
    file_size: int
    created_by: int = None


@router.post("/")
async def create_backup_record(backup: BackupCreate, request: Request):
    """Record a backup operation."""
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO backup_history (backup_date, file_name, file_size, created_by)
               VALUES ($1, $2, $3, $4) RETURNING *""",
            backup.backup_date, backup.file_name, backup.file_size, backup.created_by,
        )
    return dict(row)


@router.get("/history")
async def get_backup_history(request: Request, limit: int = 30):
    """Get backup history."""
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM backup_history ORDER BY id DESC LIMIT $1", limit
        )
    return rows_to_dicts(rows)


@router.delete("/{backup_id}")
async def delete_backup_record(backup_id: int, request: Request):
    """Delete a backup record."""
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM backup_history WHERE id = $1", backup_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Backup record not found")
    return {"message": "Backup record deleted"}


# ── pg_dump based backup ──────────────────────────────────────

@router.post("/create")
async def create_postgres_backup(request: Request):
    """Run pg_dump to create a SQL dump file, store it, and record in history."""
    user = get_current_user(request)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"backup_{now}.sql"
    file_path = BACKUP_DIR / file_name

    try:
        result = subprocess.run(
            ["pg_dump", _RAW_DB_URL, "-f", str(file_path), "--no-owner", "--no-privileges"],
            capture_output=True, text=True, timeout=120, env=_psql_env(),
        )
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"pg_dump failed: {result.stderr[:500]}")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="pg_dump not found on server")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="pg_dump timed out")

    file_size = file_path.stat().st_size

    pool = get_pool(request)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO backup_history (backup_date, file_name, file_size, created_by)
               VALUES ($1, $2, $3, $4) RETURNING *""",
            now, file_name, file_size, user.get("user_id"),
        )

    return {**dict(row), "file_path": str(file_path)}


@router.get("/download/{file_name}")
async def download_backup(file_name: str, request: Request):
    """Download a backup dump file."""
    get_current_user(request)
    file_path = BACKUP_DIR / file_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Backup file not found")
    return FileResponse(
        path=str(file_path),
        filename=file_name,
        media_type="application/sql",
    )


# ── Safe restore via temp-database swap ───────────────────────

# Tables that MUST exist in a valid restore.  Used for validation.
_CRITICAL_TABLES = [
    "users", "products", "sales", "sale_items",
    "stock_purchases", "firms", "firm_debts",
    "categories", "employees", "expenses",
    "backup_history", "notifications", "shop_settings",
    "attendance", "settings", "cash_incomes", "debt_payments",
    "firm_debt_payments", "inventory_logs",
]


async def _count_tables(dbname: str) -> int:
    """Return the number of user tables in the given database."""
    r = subprocess.run(
        _psql_admin_args(dbname) + [
            "-t", "-A", "-c",
            "SELECT count(*) FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'",
        ],
        capture_output=True, text=True, timeout=15, env=_psql_env(),
    )
    return int(r.stdout.strip()) if r.returncode == 0 else -1


async def _get_table_names(dbname: str) -> set:
    """Return the set of table names in the public schema."""
    r = subprocess.run(
        _psql_admin_args(dbname) + [
            "-t", "-A", "-c",
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'",
        ],
        capture_output=True, text=True, timeout=15, env=_psql_env(),
    )
    if r.returncode != 0:
        return set()
    return {line.strip() for line in r.stdout.strip().splitlines() if line.strip()}


async def _db_exists(dbname: str) -> bool:
    r = subprocess.run(
        _psql_admin_args("postgres") + [
            "-t", "-A", "-c",
            f"SELECT 1 FROM pg_database WHERE datname = '{dbname}'",
        ],
        capture_output=True, text=True, timeout=10, env=_psql_env(),
    )
    return r.stdout.strip() == "1"


async def _drop_db_if_exists(dbname: str):
    # Terminate active connections first
    subprocess.run(
        _psql_admin_args("postgres") + [
            "-c",
            f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            f"WHERE datname = '{dbname}' AND pid <> pg_backend_pid()",
        ],
        capture_output=True, text=True, timeout=10, env=_psql_env(),
    )
    subprocess.run(
        _psql_admin_args("postgres") + ["-c", f'DROP DATABASE IF EXISTS "{dbname}"'],
        capture_output=True, text=True, timeout=30, env=_psql_env(),
    )


async def _auto_backup(live_db: str, BACKUP_DIR) -> str | None:
    """Create a safety-net backup of the live database before a restore.
    Returns the backup file path, or None on failure."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = BACKUP_DIR / f"pre_restore_backup_{now}.sql"
    try:
        # Connect to the live database directly using parsed credentials
        result = subprocess.run(
            [
                "pg_dump",
                "-h", _DB.get("host", "localhost"),
                "-p", _DB.get("port", "5432"),
                "-U", _DB.get("user", "pos_user"),
                "-d", live_db,
                "-f", str(file_path),
                "--no-owner", "--no-privileges",
            ],
            capture_output=True, text=True, timeout=120, env=_psql_env(),
        )
        if result.returncode == 0 and file_path.exists() and file_path.stat().st_size > 0:
            return str(file_path)
    except Exception:
        pass
    return None


async def _validate_restore(temp_db: str, live_db: str) -> list[str]:
    """Validate the restored temp database. Returns a list of error messages
    (empty list means validation passed)."""
    errors = []

    # 1. Check that the temp DB has at least as many tables as the live DB
    live_count = await _count_tables(live_db)
    temp_count = await _count_tables(temp_db)
    if live_count > 0 and temp_count < live_count:
        errors.append(
            f"Temp database has {temp_count} tables but live DB has {live_count} — "
            f"dump may be incomplete"
        )

    # 2. Check that every critical table exists in the temp DB
    temp_tables = await _get_table_names(temp_db)
    missing = [t for t in _CRITICAL_TABLES if t not in temp_tables]
    if missing:
        errors.append(f"Missing critical tables: {', '.join(missing)}")

    return errors


@router.post("/restore")
async def restore_postgres_backup(request: Request, file: UploadFile = File(...)):
    """Safely restore the database from an uploaded SQL dump.

    Strategy — temp-database swap with auto-backup safety net:
      0. Create an auto-backup of the live database (safety net).
      1. Save the uploaded SQL to a file on disk.
      2. Create a *temporary* database (pos_db_restore_XXXX).
      3. Restore the dump into that temp database.
      4. Validate the temp database thoroughly:
         a. Table count >= live DB table count.
         b. All critical tables exist.
      5. Only THEN: drop the old live database and rename temp → live.
      6. If swap fails, attempt recovery from auto-backup.

    At no point is the live database destroyed before the replacement is
    confirmed valid.
    """
    get_current_user(request)

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    # ── Step 0: Auto-backup current database (safety net) ──────
    live_db = _DB.get("dbname", "pos_db")
    auto_backup_path = await _auto_backup(live_db, BACKUP_DIR)

    # ── Step 1: Save uploaded dump to disk ─────────────────────
    # Strip SET statements that newer pg_dump emits but older servers reject
    # (e.g. "SET transaction_timeout = 0" from PG17 against a PG16 server).
    sql_text = content.decode("utf-8", errors="replace")
    sql_text = re.sub(r"(?m)^SET transaction_timeout\s*=.*$", "", sql_text)
    content = sql_text.encode("utf-8")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    temp_dump = BACKUP_DIR / f"_restore_{uuid.uuid4().hex[:8]}.sql"
    temp_dump.write_bytes(content)

    temp_db = f"{live_db}_restore_{uuid.uuid4().hex[:8]}"
    errors = []
    swapped = False

    try:
        # ── Step 2: Create temporary database ──────────────────
        r = subprocess.run(
            _psql_admin_args("postgres") + ["-c", f'CREATE DATABASE "{temp_db}"'],
            capture_output=True, text=True, timeout=15, env=_psql_env(),
        )
        if r.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create temp database: {r.stderr[:300]}",
            )

        # ── Step 3: Restore dump into temp database ────────────
        # Use ON_ERROR_STOP=1 so psql aborts on the first SQL error.
        # NOTE: --no-owner / --no-privileges are pg_dump flags, NOT psql flags.
        r = subprocess.run(
            _psql_admin_args(temp_db) + [
                "-v", "ON_ERROR_STOP=1",
                "-f", str(temp_dump),
            ],
            capture_output=True, text=True, timeout=300, env=_psql_env(),
        )
        if r.returncode != 0:
            # Include both stderr and the tail of stdout for debugging
            combined = (r.stderr + "\n" + r.stdout)[-800:]
            errors.append(f"psql restore error: {combined}")
            raise Exception("psql returned non-zero exit code")

        # ── Step 4: Thorough validation ───────────────────────
        errors = await _validate_restore(temp_db, live_db)
        if errors:
            raise Exception("Validation failed: " + "; ".join(errors))

        table_count = await _count_tables(temp_db)

        # ── Step 5: Swap — drop live, rename temp → live ───────
        await _drop_db_if_exists(live_db)
        swapped = True

        r = subprocess.run(
            _psql_admin_args("postgres") + [
                "-c", f'ALTER DATABASE "{temp_db}" RENAME TO "{live_db}"',
            ],
            capture_output=True, text=True, timeout=15, env=_psql_env(),
        )
        if r.returncode != 0:
            # Recovery: try to restore from the auto-backup we created
            recovered = False
            if auto_backup_path and await _db_exists("postgres"):
                # Recreate live DB empty first, then restore from auto-backup
                subprocess.run(
                    _psql_admin_args("postgres") + [
                        "-c", f'CREATE DATABASE "{live_db}"',
                    ],
                    capture_output=True, text=True, timeout=15, env=_psql_env(),
                )
                rec = subprocess.run(
                    _psql_admin_args(live_db) + [
                        "-v", "ON_ERROR_STOP=1",
                        "-f", auto_backup_path,
                    ],
                    capture_output=True, text=True, timeout=300, env=_psql_env(),
                )
                recovered = rec.returncode == 0

            raise HTTPException(
                status_code=500,
                detail=(
                    f"Rename failed after dropping live DB: {r.stderr[:300]}. "
                    + ("Recovered from auto-backup." if recovered
                       else "Auto-backup recovery also failed — "
                           f"manual restore from {auto_backup_path or 'N/A'} required.")
                ),
            )

        return {
            "message": "Database restored successfully",
            "file_name": file.filename,
            "tables_restored": table_count,
            "auto_backup": auto_backup_path,
        }

    except HTTPException:
        raise
    except Exception as e:
        msg = errors[-1] if errors else str(e)
        # Clean up the temp database if it still exists (only if we didn't swap)
        if not swapped:
            await _drop_db_if_exists(temp_db)
        raise HTTPException(status_code=500, detail=f"Restore failed: {msg}")

    finally:
        # Always clean up the temp dump file from disk
        if temp_dump.exists():
            temp_dump.unlink()
