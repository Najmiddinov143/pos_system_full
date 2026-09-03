#!/usr/bin/env python3
"""
One-time migration: import products from old SQLite database into PostgreSQL.

Reads from database/pos.db, inserts into the current PostgreSQL schema.
Safe to run twice — skips duplicates by product name.
"""

import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime


# ── Config ─────────────────────────────────────────────────────

SQLITE_PATH = "database/pos.db"

RAW_DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pos_user:pos_password@localhost:5432/pos_db",
)

# Map SQLite category strings to existing PG category names.
# Unmapped categories are left as NULL (category_id not set).
CATEGORY_MAP = {
    "Moy": "Moylar",           # "Moy" → "Moylar" (oils)
    "Motor flush": None,        # Will create new category
    "dot4": None,               # Will create new category
}


# ── Helpers ────────────────────────────────────────────────────

def parse_db_url(url):
    m = re.match(r"postgresql://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/(.+)", url)
    if not m:
        sys.exit(f"Cannot parse DATABASE_URL: {url}")
    return {
        "user": m.group(1), "password": m.group(2),
        "host": m.group(3), "port": m.group(4) or "5432",
        "dbname": m.group(5),
    }


def psql_env(db):
    env = os.environ.copy()
    env["PGPASSWORD"] = db["password"]
    return env


def psql_args(db, dbname=None):
    return [
        "psql", "-h", db["host"], "-p", db["port"],
        "-U", db["user"], "-d", dbname or db["dbname"],
        "-t", "-A",
    ]


def psql_query(sql, db, dbname=None):
    r = subprocess.run(
        psql_args(db, dbname) + ["-c", sql],
        capture_output=True, text=True, timeout=15, env=psql_env(db),
    )
    return r.stdout.strip() if r.returncode == 0 else None


def psql_execute(sql, db):
    r = subprocess.run(
        psql_args(db) + ["-c", sql],
        capture_output=True, text=True, timeout=30, env=psql_env(db),
    )
    if r.returncode != 0:
        print(f"  ⚠️  SQL error: {r.stderr[:300]}")
    return r.returncode == 0


def psql_insert(sql, db):
    """Execute an INSERT and return the new id, or None on failure."""
    r = subprocess.run(
        psql_args(db) + ["-c", sql],
        capture_output=True, text=True, timeout=15, env=psql_env(db),
    )
    if r.returncode != 0:
        print(f"  ⚠️  INSERT error: {r.stderr[:200]}")
        return None
    # psql -t -A returns: "<id>\nINSERT 0 1" — take only the first line
    first_line = r.stdout.strip().splitlines()[0].strip()
    return int(first_line) if first_line.isdigit() else None


# ── Main ───────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("🔄  SQLITE → POSTGRESQL MIGRATION")
    print("=" * 60)
    print(f"Source: {SQLITE_PATH}")
    print(f"Target: {RAW_DB_URL.split('@')[-1] if '@' in RAW_DB_URL else RAW_DB_URL}")
    print(f"Time:   {datetime.now().isoformat()}")
    print()

    db = parse_db_url(RAW_DB_URL)

    # ── Open SQLite ──
    if not os.path.exists(SQLITE_PATH):
        sys.exit(f"❌ SQLite file not found: {SQLITE_PATH}")

    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    cur = sqlite_conn.cursor()

    # ── Check tables exist ──
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    sqlite_tables = {r["name"] for r in cur.fetchall()}
    print(f"SQLite tables: {sorted(sqlite_tables)}")
    print()

    if "products" not in sqlite_tables:
        sys.exit("❌ No 'products' table in SQLite file")

    # ── Get existing PG products (for dedup) ──
    pg_names_raw = psql_query(
        "SELECT name FROM products", db
    )
    pg_existing_names = set()
    if pg_names_raw:
        pg_existing_names = {line.strip() for line in pg_names_raw.splitlines() if line.strip()}
    print(f"PostgreSQL existing products: {len(pg_existing_names)}")
    print()

    # ── Get PG categories ──
    pg_cats_raw = psql_query("SELECT id, name FROM categories ORDER BY id", db)
    pg_categories = {}  # name -> id
    if pg_cats_raw:
        for line in pg_cats_raw.splitlines():
            if "|" in line:
                cid, cname = line.split("|", 1)
                pg_categories[cname.strip()] = int(cid.strip())
    print(f"PostgreSQL categories: {pg_categories}")
    print()

    # ── Resolve category IDs for unmapped SQLite categories ──
    cur.execute("SELECT DISTINCT category FROM products WHERE category != ''")
    sqlite_categories = [r["category"] for r in cur.fetchall()]

    def _ensure_category(name):
        """Return PG category id for `name`. Create it if it doesn't exist."""
        safe = name.replace("'", "''")
        existing = psql_query(f"SELECT id FROM categories WHERE name = '{safe}'", db)
        if existing and existing.isdigit():
            return int(existing)
        new_id = psql_insert(
            f"INSERT INTO categories (name) VALUES ('{safe}') RETURNING id", db
        )
        return new_id

    category_id_cache = {}  # sqlite_category -> pg_category_id or None
    for sqlite_cat in sqlite_categories:
        mapped_name = CATEGORY_MAP.get(sqlite_cat)
        if sqlite_cat not in CATEGORY_MAP and mapped_name is None:
            # Not mentioned in CATEGORY_MAP at all — leave as NULL
            category_id_cache[sqlite_cat] = None
            continue

        # Determine target PG category name
        target_name = mapped_name if mapped_name else sqlite_cat
        cat_id = _ensure_category(target_name)
        if cat_id:
            pg_categories[target_name] = cat_id
            category_id_cache[sqlite_cat] = cat_id
            print(f"  ℹ️  Category '{sqlite_cat}' → '{target_name}' (id={cat_id})")
        else:
            print(f"  ⚠️  Failed to resolve category: {sqlite_cat}")
            category_id_cache[sqlite_cat] = None
    print()

    # ── Import products ──
    cur.execute("""
        SELECT id, name, category, cost_price, sell_price, quantity, unit,
               min_quantity, note, image_path, barcode, supplier,
               is_active, dollar_cost, dollar_price, exchange_rate
        FROM products
        ORDER BY id
    """)
    sqlite_products = cur.fetchall()
    print(f"SQLite products to import: {len(sqlite_products)}")
    print()

    imported = 0
    skipped_dup = 0
    errors = 0

    for prod in sqlite_products:
        name = prod["name"].strip()
        if not name:
            continue

        # Dedup check
        if name in pg_existing_names:
            skipped_dup += 1
            continue

        # Resolve category_id
        sqlite_cat = prod["category"] or ""
        cat_id = category_id_cache.get(sqlite_cat)

        # Escape strings for SQL
        def esc(val):
            if val is None:
                return "NULL"
            s = str(val).replace("'", "''")
            return f"'{s}'"

        def num(val):
            if val is None:
                return "0"
            return str(float(val))

        cat_id_sql = str(cat_id) if cat_id else "NULL"

        sql = f"""INSERT INTO products (
            name, category, cost_price, sell_price, quantity, unit,
            min_quantity, note, image_path, barcode, supplier,
            is_active, dollar_cost, dollar_price, exchange_rate, category_id
        ) VALUES (
            {esc(name)}, {esc(sqlite_cat)}, {num(prod['cost_price'])}, {num(prod['sell_price'])},
            {num(prod['quantity'])}, {esc(prod['unit'])}, {num(prod['min_quantity'])},
            {esc(prod['note'])}, {esc(prod['image_path'])}, {esc(prod['barcode'])},
            {esc(prod['supplier'])}, {int(prod['is_active'] or 1)},
            {num(prod['dollar_cost'])}, {num(prod['dollar_price'])}, {num(prod['exchange_rate'])},
            {cat_id_sql}
        ) RETURNING id"""

        new_id = psql_insert(sql, db)
        if new_id:
            pg_existing_names.add(name)  # prevent intra-batch dupes
            imported += 1
        else:
            errors += 1

    # ── Import other tables ──
    other_imported = {}

    # firms (if present)
    if "firms" in sqlite_tables:
        cur.execute("SELECT * FROM firms")
        firms = cur.fetchall()
        for firm in firms:
            safe_name = (firm["name"] or "").replace("'", "''")
            # Skip if already exists
            check = psql_query(
                f"SELECT 1 FROM firms WHERE name = '{safe_name}'", db
            )
            if check:
                continue
            sql = f"""INSERT INTO firms (name, phone, address, total_debt, note)
                VALUES ({esc(firm['name'])}, {esc(firm['phone'])}, {esc(firm['address'])},
                        {num(firm['total_debt'])}, {esc(firm['note'])}) RETURNING id"""
            if psql_insert(sql, db):
                other_imported.setdefault("firms", 0)
                other_imported["firms"] += 1

    # employees (if present and not already in PG)
    if "employees" in sqlite_tables:
        cur.execute("SELECT * FROM employees")
        emps = cur.fetchall()
        for emp in emps:
            safe_name = (emp["full_name"] or "").replace("'", "''")
            check = psql_query(
                f"SELECT 1 FROM employees WHERE full_name = '{safe_name}'", db
            )
            if check:
                continue
            sql = f"""INSERT INTO employees (full_name, phone, position, salary, hire_date, is_active)
                VALUES ({esc(emp['full_name'])}, {esc(emp['phone'])}, {esc(emp['position'])},
                        {num(emp['salary'])}, {esc(emp['hire_date'])}, {int(emp['is_active'] or 1)})
                RETURNING id"""
            if psql_insert(sql, db):
                other_imported.setdefault("employees", 0)
                other_imported["employees"] += 1

    # settings (if present)
    if "settings" in sqlite_tables:
        cur.execute("SELECT * FROM settings")
        settings = cur.fetchall()
        for s in settings:
            safe_key = (s["key"] or "").replace("'", "''")
            check = psql_query(
                f"SELECT 1 FROM settings WHERE key = '{safe_key}'", db
            )
            if check:
                continue
            sql = f"""INSERT INTO settings (key, value)
                VALUES ({esc(s['key'])}, {esc(s['value'])}) RETURNING id"""
            if psql_insert(sql, db):
                other_imported.setdefault("settings", 0)
                other_imported["settings"] += 1

    sqlite_conn.close()

    # ── Summary ──
    print()
    print("=" * 60)
    print("📊  MIGRATION SUMMARY")
    print("=" * 60)
    print(f"  Products imported:    {imported}")
    print(f"  Products skipped:     {skipped_dup} (duplicates)")
    print(f"  Product errors:       {errors}")
    for table, count in other_imported.items():
        print(f"  {table.title():20s} imported: {count}")
    print()

    # Verify
    pg_count = psql_query("SELECT count(*) FROM products", db)
    pg_active = psql_query("SELECT count(*) FROM products WHERE is_active = 1", db)
    pg_cats = psql_query("SELECT count(*) FROM categories", db)
    print(f"  PostgreSQL products now: {pg_count} total, {pg_active} active")
    print(f"  PostgreSQL categories:   {pg_cats}")
    print()

    if imported > 0:
        print("🟢 Migration complete!")
    elif skipped_dup > 0 and imported == 0:
        print("🟡 All products already exist — nothing to import.")
    else:
        print("🔴 No data was imported. Check errors above.")


if __name__ == "__main__":
    main()
