#!/usr/bin/env python3
"""
Backup Restore Safety Tests

Verifies the restore process:
  1. Restore doesn't destroy the schema (all 19 tables survive)
  2. Restore actually reverts data to the backup point
  3. Corrupted dumps are rejected without breaking the DB
  4. App API recovers after restore (pool reconnection)

Strategy:
  - Uses direct psql for schema verification (bypasses app pool)
  - Uses app API for data-level checks (tests pool recovery)
  - Creates/restores real backups via the API
"""

import os
import re
import subprocess
import sys
import time
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_KEY = None

PASS = 0
FAIL = 0
_DB = {}


def log_pass(msg):
    global PASS
    PASS += 1
    print(f"  ✅ {msg}")


def log_fail(msg, detail=""):
    global FAIL
    FAIL += 1
    print(f"  ❌ {msg}")
    if detail:
        print(f"     → {detail}")


def log_info(msg):
    print(f"  ℹ️  {msg}")


def auth_headers():
    return {"X-API-Key": API_KEY}


def setup_login():
    global API_KEY
    print("\n🔑 Logging in as admin...")
    r = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "admin", "password": "admin123"
    }, timeout=10)
    if r.status_code != 200:
        print(f"❌ Login failed: {r.status_code} {r.text}")
        sys.exit(1)
    API_KEY = r.json()["api_key"]
    log_pass(f"Logged in (user_id={r.json()['id']})")


def parse_db_url():
    """Parse DATABASE_URL from environment for direct psql calls."""
    global _DB
    url = os.getenv("DATABASE_URL", "postgresql://pos_user:pos_password@localhost:5432/pos_db")
    m = re.match(r"postgresql://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/(.+)", url)
    if m:
        _DB = {
            "user": m.group(1), "password": m.group(2),
            "host": m.group(3), "port": m.group(4) or "5432",
            "dbname": m.group(5),
        }


def psql_env():
    env = os.environ.copy()
    if _DB.get("password"):
        env["PGPASSWORD"] = _DB["password"]
    return env


def psql_args(dbname=None):
    return [
        "psql", "-h", _DB.get("host", "localhost"),
        "-p", _DB.get("port", "5432"),
        "-U", _DB.get("user", "pos_user"),
        "-d", dbname or _DB.get("dbname", "pos_db"),
        "-t", "-A",
    ]


def psql_query(sql, dbname=None):
    """Run a SQL query via psql and return stripped output."""
    r = subprocess.run(
        psql_args(dbname) + ["-c", sql],
        capture_output=True, text=True, timeout=15, env=psql_env(),
    )
    return r.stdout.strip() if r.returncode == 0 else None


def get_table_names(dbname=None):
    """Return set of table names in the public schema."""
    out = psql_query(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'",
        dbname,
    )
    if out is None:
        return set()
    return {line.strip() for line in out.splitlines() if line.strip()}


def count_rows(table, dbname=None):
    """Return row count for a table."""
    out = psql_query(f"SELECT count(*) FROM {table}", dbname)
    return int(out) if out is not None else -1


# ════════════════════════════════════════════════════════════════
#  Expected schema
# ════════════════════════════════════════════════════════════════

EXPECTED_TABLES = {
    "users", "products", "sales", "sale_items",
    "stock_purchases", "firms", "firm_debts",
    "categories", "employees", "expenses",
    "backup_history", "notifications", "shop_settings",
    "attendance", "settings", "cash_incomes", "debt_payments",
    "firm_debt_payments", "inventory_logs",
}


def api_with_retry(method, url, retries=5, delay=2, **kwargs):
    """Call the API with retries — needed after restore kills pool connections."""
    kwargs.setdefault("timeout", 10)
    for attempt in range(retries):
        try:
            r = getattr(requests, method)(url, **kwargs)
            if r.status_code < 500:
                return r
        except requests.ConnectionError:
            pass
        if attempt < retries - 1:
            time.sleep(delay)
    # Final attempt, return whatever we get
    return getattr(requests, method)(url, **kwargs)


# ════════════════════════════════════════════════════════════════
#  TEST 1: Schema survival after restore
# ════════════════════════════════════════════════════════════════

def test_schema_survives_restore():
    print("\n" + "=" * 60)
    print("🛡️   TEST 1: Schema survives restore")
    print("=" * 60)

    # Snapshot schema BEFORE backup
    tables_before = get_table_names()
    log_info(f"Tables before backup: {len(tables_before)}")

    missing_before = EXPECTED_TABLES - tables_before
    if missing_before:
        log_fail(f"Schema already incomplete before test — missing: {missing_before}")
        return
    log_pass(f"All {len(EXPECTED_TABLES)} expected tables present before backup")

    # Create backup
    log_info("Creating backup via POST /api/backup/create ...")
    r = requests.post(f"{BASE_URL}/api/backup/create", headers=auth_headers(), timeout=120)
    if r.status_code != 200:
        log_fail(f"Backup creation failed → {r.status_code}", r.text[:300])
        return
    backup_data = r.json()
    backup_filename = backup_data.get("file_name")
    log_pass(f"Backup created: {backup_filename} ({backup_data.get('file_size', '?')} bytes)")

    # Add a test product so we can verify data after restore
    log_info("Adding test product RESTORE_TEST_001 ...")
    r = requests.post(f"{BASE_URL}/api/products/", json={
        "name": "RESTORE_TEST_001",
        "category": "RestoreTest",
        "cost_price": 99.99,
        "sell_price": 199.99,
        "quantity": 42,
    }, headers=auth_headers(), timeout=10)
    if r.status_code != 200:
        log_fail(f"Create test product failed → {r.status_code}", r.text[:200])
        return
    test_pid = r.json()["id"]
    log_pass(f"Test product created id={test_pid}")

    # Verify it exists via API
    r = requests.get(f"{BASE_URL}/api/products/{test_pid}", headers=auth_headers(), timeout=10)
    if r.status_code == 200 and r.json()["name"] == "RESTORE_TEST_001":
        log_pass("Test product verified via API before restore")
    else:
        log_fail("Test product not found before restore")

    # Also check via direct psql that stock_purchases exists and is queryable
    sp_count = count_rows("stock_purchases")
    log_info(f"stock_purchases has {sp_count} rows before restore")

    # ── RESTORE ────────────────────────────────────────────────
    log_info("Downloading backup file ...")
    r = requests.get(f"{BASE_URL}/api/backup/download/{backup_filename}",
                     headers=auth_headers(), timeout=30)
    if r.status_code != 200:
        log_fail(f"Download backup failed → {r.status_code}")
        return
    backup_content = r.content
    log_pass(f"Downloaded backup ({len(backup_content)} bytes)")

    log_info("Restoring from backup ...")
    r = requests.post(
        f"{BASE_URL}/api/backup/restore",
        files={"file": (backup_filename, backup_content, "application/sql")},
        headers=auth_headers(),
        timeout=300,
    )
    if r.status_code == 200:
        result = r.json()
        log_pass(f"Restore succeeded: {result.get('tables_restored', '?')} tables restored")
        log_info(f"Auto-backup saved to: {result.get('auto_backup', 'N/A')}")
    else:
        log_fail(f"Restore failed → {r.status_code}", r.text[:500])
        # Don't return — still check schema survival even on failure

    # ── VERIFY SCHEMA ──────────────────────────────────────────
    # Wait briefly for pool to recover
    log_info("Waiting 3s for connection pool to recover ...")
    time.sleep(3)

    tables_after = get_table_names()
    log_info(f"Tables after restore: {len(tables_after)}")

    missing_after = EXPECTED_TABLES - tables_after
    if missing_after:
        log_fail(f"CRITICAL: Tables missing after restore: {missing_after}")
    else:
        log_pass(f"All {len(EXPECTED_TABLES)} expected tables present after restore")

    # Check for unexpected extra tables
    extra = tables_after - EXPECTED_TABLES
    if extra:
        log_info(f"Extra tables found (OK, may be from other features): {extra}")

    # ── Verify stock_purchases specifically (the one that broke before) ──
    if "stock_purchases" in tables_after:
        sp_count_after = count_rows("stock_purchases")
        log_pass(f"stock_purchases exists after restore ({sp_count_after} rows)")
    else:
        log_fail("CRITICAL: stock_purchases table MISSING after restore!")

    # Check every critical table is queryable
    for table in sorted(EXPECTED_TABLES):
        if table in tables_after:
            cnt = count_rows(table)
            if cnt >= 0:
                pass  # OK, queryable
            else:
                log_fail(f"Table {table} exists but is not queryable")
        else:
            log_fail(f"Table {table} MISSING")

    # ── Verify test product is GONE (backup was taken before it was created) ──
    r = api_with_retry("get", f"{BASE_URL}/api/products/{test_pid}",
                       headers=auth_headers(), timeout=10)
    if r.status_code == 404:
        log_pass(f"Test product id={test_pid} correctly absent after restore (reverted to backup state)")
    elif r.status_code == 200:
        log_fail(f"Test product id={test_pid} still exists — restore may not have worked")
    else:
        log_fail(f"Check test product → {r.status_code}", r.text[:200])

    # ── Verify app API works post-restore ──
    log_info("Verifying app API works after restore ...")
    r = api_with_retry("get", f"{BASE_URL}/api/products/",
                       headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        log_pass(f"GET /api/products/ works after restore ({len(r.json())} products)")
    else:
        log_fail(f"GET /api/products/ broken after restore → {r.status_code}")


# ════════════════════════════════════════════════════════════════
#  TEST 2: Data round-trip (backup captures, restore brings back)
# ════════════════════════════════════════════════════════════════

def test_data_roundtrip():
    print("\n" + "=" * 60)
    print("🔄  TEST 2: Data round-trip (backup → add data → restore → verify)")
    print("=" * 60)

    # Step A: Create a product BEFORE backup (so it's in the backup)
    log_info("Creating product ROUNDTRIP_SEED (will be in backup) ...")
    r = requests.post(f"{BASE_URL}/api/products/", json={
        "name": "ROUNDTRIP_SEED",
        "category": "RoundtripTest",
        "cost_price": 10,
        "sell_price": 20,
        "quantity": 100,
    }, headers=auth_headers(), timeout=10)
    if r.status_code != 200:
        log_fail(f"Create seed product failed → {r.status_code}")
        return
    seed_pid = r.json()["id"]
    log_pass(f"Seed product created id={seed_pid}")

    # Step B: Create backup (includes seed product)
    log_info("Creating backup with seed product ...")
    r = requests.post(f"{BASE_URL}/api/backup/create", headers=auth_headers(), timeout=120)
    if r.status_code != 200:
        log_fail(f"Backup failed → {r.status_code}")
        return
    backup_filename = r.json()["file_name"]
    log_pass(f"Backup created: {backup_filename}")

    # Step C: Add MORE data AFTER backup (should be lost on restore)
    log_info("Adding post-backup product ROUNDTRIP_POST ...")
    r = requests.post(f"{BASE_URL}/api/products/", json={
        "name": "ROUNDTRIP_POST",
        "category": "RoundtripTest",
        "cost_price": 30,
        "sell_price": 60,
        "quantity": 50,
    }, headers=auth_headers(), timeout=10)
    if r.status_code != 200:
        log_fail(f"Create post-backup product failed → {r.status_code}")
        return
    post_pid = r.json()["id"]
    log_pass(f"Post-backup product created id={post_pid}")

    # Verify both exist
    r1 = requests.get(f"{BASE_URL}/api/products/{seed_pid}", headers=auth_headers(), timeout=10)
    r2 = requests.get(f"{BASE_URL}/api/products/{post_pid}", headers=auth_headers(), timeout=10)
    if r1.status_code == 200 and r2.status_code == 200:
        log_pass("Both products exist before restore")
    else:
        log_fail("Products not found before restore")

    # Step D: Restore from backup
    log_info("Downloading backup ...")
    r = requests.get(f"{BASE_URL}/api/backup/download/{backup_filename}",
                     headers=auth_headers(), timeout=30)
    backup_content = r.content

    log_info("Restoring from backup ...")
    r = requests.post(
        f"{BASE_URL}/api/backup/restore",
        files={"file": (backup_filename, backup_content, "application/sql")},
        headers=auth_headers(),
        timeout=300,
    )
    if r.status_code == 200:
        log_pass(f"Restore succeeded: {r.json().get('tables_restored', '?')} tables")
    else:
        log_fail(f"Restore failed → {r.status_code}", r.text[:500])

    time.sleep(3)

    # Step E: Verify seed product EXISTS (was in backup)
    r = api_with_retry("get", f"{BASE_URL}/api/products/{seed_pid}",
                       headers=auth_headers(), timeout=10)
    if r.status_code == 200 and r.json()["name"] == "ROUNDTRIP_SEED":
        log_pass(f"Seed product id={seed_pid} exists after restore (correct)")
    else:
        log_fail(f"Seed product id={seed_pid} missing after restore (should be there)")

    # Step F: Verify post-backup product is GONE (was added after backup)
    r = api_with_retry("get", f"{BASE_URL}/api/products/{post_pid}",
                       headers=auth_headers(), timeout=10)
    if r.status_code == 404:
        log_pass(f"Post-backup product id={post_pid} correctly absent after restore")
    elif r.status_code == 200:
        log_fail(f"Post-backup product id={post_pid} still exists — restore didn't revert")
    else:
        log_fail(f"Check post-backup product → {r.status_code}")


# ════════════════════════════════════════════════════════════════
#  TEST 3: Corrupted dump is rejected safely
# ════════════════════════════════════════════════════════════════

def test_corrupted_dump_rejected():
    print("\n" + "=" * 60)
    print("🚫  TEST 3: Corrupted dump rejected safely")
    print("=" * 60)

    # Snapshot schema before
    tables_before = get_table_names()
    log_info(f"Tables before corrupted restore: {len(tables_before)}")

    # Create a product so we can verify it survives
    log_info("Creating product CORRUPT_TEST ...")
    r = requests.post(f"{BASE_URL}/api/products/", json={
        "name": "CORRUPT_TEST",
        "category": "CorruptTest",
        "cost_price": 5,
        "sell_price": 10,
        "quantity": 25,
    }, headers=auth_headers(), timeout=10)
    if r.status_code != 200:
        log_fail(f"Create test product failed → {r.status_code}")
        return
    corrupt_pid = r.json()["id"]
    log_pass(f"Test product created id={corrupt_pid}")

    # Attempt restore with garbage SQL
    log_info("Attempting restore with corrupted/garbage SQL ...")
    garbage = b"This is not valid SQL. DROP TABLE products; SELECT 1;"
    r = requests.post(
        f"{BASE_URL}/api/backup/restore",
        files={"file": ("corrupt.sql", garbage, "application/sql")},
        headers=auth_headers(),
        timeout=120,
    )
    if r.status_code == 500:
        log_pass(f"Corrupted dump correctly rejected (HTTP 500)")
        log_info(f"Error message: {r.text[:200]}")
    elif r.status_code == 200:
        log_fail("Corrupted dump was ACCEPTED — this is dangerous!")
    else:
        log_pass(f"Corrupted dump rejected (HTTP {r.status_code})")

    time.sleep(2)

    # Verify database is still intact
    tables_after = get_table_names()
    if tables_after == tables_before:
        log_pass(f"Schema intact after rejected restore ({len(tables_after)} tables)")
    else:
        missing = tables_before - tables_after
        extra = tables_after - tables_before
        if missing:
            log_fail(f"CRITICAL: Tables lost after rejected restore: {missing}")
        if extra:
            log_info(f"Extra tables appeared: {extra}")

    # Verify test product still exists
    r = api_with_retry("get", f"{BASE_URL}/api/products/{corrupt_pid}",
                       headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        log_pass(f"Product id={corrupt_pid} survived rejected restore")
    else:
        log_fail(f"Product id={corrupt_pid} gone after rejected restore!")

    # Attempt restore with empty file
    log_info("Attempting restore with empty file ...")
    r = requests.post(
        f"{BASE_URL}/api/backup/restore",
        files={"file": ("empty.sql", b"", "application/sql")},
        headers=auth_headers(),
        timeout=30,
    )
    if r.status_code in (400, 500):
        log_pass(f"Empty file correctly rejected (HTTP {r.status_code})")
    else:
        log_fail(f"Empty file accepted (HTTP {r.status_code})")


# ════════════════════════════════════════════════════════════════
#  TEST 4: Restore handles edge cases
# ════════════════════════════════════════════════════════════════

def test_restore_edge_cases():
    print("\n" + "=" * 60)
    print("Edge cases: multiple sequential restores")
    print("=" * 60)

    # Create a marker product
    log_info("Creating marker product EDGE_001 ...")
    r = requests.post(f"{BASE_URL}/api/products/", json={
        "name": "EDGE_001",
        "cost_price": 1,
        "sell_price": 2,
        "quantity": 10,
    }, headers=auth_headers(), timeout=10)
    if r.status_code != 200:
        log_fail(f"Create marker failed → {r.status_code}")
        return
    edge_pid = r.json()["id"]
    log_pass(f"Marker product id={edge_pid}")

    # Backup 1 (contains EDGE_001)
    log_info("Creating backup_1 (with EDGE_001) ...")
    r = requests.post(f"{BASE_URL}/api/backup/create", headers=auth_headers(), timeout=120)
    if r.status_code != 200:
        log_fail(f"backup_1 failed → {r.status_code}")
        return
    backup1_name = r.json()["file_name"]
    log_pass(f"backup_1: {backup1_name}")

    # Add second marker
    log_info("Creating marker product EDGE_002 ...")
    r = requests.post(f"{BASE_URL}/api/products/", json={
        "name": "EDGE_002",
        "cost_price": 3,
        "sell_price": 6,
        "quantity": 20,
    }, headers=auth_headers(), timeout=10)
    if r.status_code != 200:
        log_fail(f"Create marker 2 failed → {r.status_code}")
        return
    edge_pid2 = r.json()["id"]
    log_pass(f"Marker product 2 id={edge_pid2}")

    # Download backup_1
    r = requests.get(f"{BASE_URL}/api/backup/download/{backup1_name}",
                     headers=auth_headers(), timeout=30)
    backup1_content = r.content

    # ── First restore ──
    log_info("First restore (should lose EDGE_002, keep EDGE_001) ...")
    r = requests.post(
        f"{BASE_URL}/api/backup/restore",
        files={"file": (backup1_name, backup1_content, "application/sql")},
        headers=auth_headers(), timeout=300,
    )
    if r.status_code == 200:
        log_pass("First restore succeeded")
    else:
        log_fail(f"First restore failed → {r.status_code}", r.text[:300])
        return

    time.sleep(3)

    r = api_with_retry("get", f"{BASE_URL}/api/products/{edge_pid}",
                       headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        log_pass("EDGE_001 exists after first restore")
    else:
        log_fail("EDGE_001 missing after first restore")

    r = api_with_retry("get", f"{BASE_URL}/api/products/{edge_pid2}",
                       headers=auth_headers(), timeout=10)
    if r.status_code == 404:
        log_pass("EDGE_002 correctly gone after first restore")
    else:
        log_fail(f"EDGE_002 still present after first restore (status={r.status_code})")

    # ── Second sequential restore (same backup) ──
    log_info("Second sequential restore (same backup_1) ...")
    r = requests.post(
        f"{BASE_URL}/api/backup/restore",
        files={"file": (backup1_name, backup1_content, "application/sql")},
        headers=auth_headers(), timeout=300,
    )
    if r.status_code == 200:
        log_pass("Second restore succeeded")
    else:
        log_fail(f"Second restore failed → {r.status_code}", r.text[:300])
        return

    time.sleep(3)

    # Schema still intact?
    tables = get_table_names()
    missing = EXPECTED_TABLES - tables
    if not missing:
        log_pass(f"All {len(EXPECTED_TABLES)} tables survive double restore")
    else:
        log_fail(f"Tables missing after double restore: {missing}")

    # stock_purchases queryable?
    sp = count_rows("stock_purchases")
    if sp >= 0:
        log_pass(f"stock_purchases queryable after double restore ({sp} rows)")
    else:
        log_fail("stock_purchases not queryable after double restore")


# ════════════════════════════════════════════════════════════════
#  CLEANUP
# ════════════════════════════════════════════════════════════════

def cleanup():
    print("\n" + "=" * 60)
    print("🧹  CLEANUP")
    print("=" * 60)

    # Find and soft-delete all test products
    test_names = [
        "RESTORE_TEST_001", "ROUNDTRIP_SEED", "ROUNDTRIP_POST",
        "CORRUPT_TEST", "EDGE_001", "EDGE_002",
    ]
    r = requests.get(f"{BASE_URL}/api/products/", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        for p in r.json():
            if p["name"] in test_names:
                dr = requests.delete(f"{BASE_URL}/api/products/{p['id']}",
                                     headers=auth_headers(), timeout=10)
                if dr.status_code == 200:
                    log_pass(f"Cleaned up product {p['name']} (id={p['id']})")
                else:
                    print(f"  ⚠️  Could not delete {p['name']}: {dr.status_code}")


# ════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("🧪  BACKUP RESTORE SAFETY TESTS")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Time:   {datetime.now().isoformat()}")

    parse_db_url()

    # Check server
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if r.status_code != 200:
            print(f"❌ Server not healthy: {r.status_code}")
            sys.exit(1)
        print("✅ Server is healthy")
    except requests.ConnectionError:
        print(f"❌ Cannot connect to {BASE_URL}")
        sys.exit(1)

    # Check psql is available
    try:
        subprocess.run(["psql", "--version"], capture_output=True, timeout=5)
    except FileNotFoundError:
        print("❌ psql not found — needed for direct schema verification")
        sys.exit(1)
    print("✅ psql available for direct DB verification")

    # Check we can query the DB directly
    tables = get_table_names()
    if not tables:
        print("❌ Cannot query database directly via psql")
        sys.exit(1)
    print(f"✅ Direct DB access works ({len(tables)} tables)")

    setup_login()

    test_schema_survives_restore()
    test_data_roundtrip()
    test_corrupted_dump_rejected()
    test_restore_edge_cases()
    cleanup()

    total = PASS + FAIL
    print("\n" + "=" * 60)
    print(f"📊  RESULTS: {PASS}/{total} passed, {FAIL}/{total} failed")
    print("=" * 60)

    if FAIL > 0:
        print("🔴 SOME TESTS FAILED")
        sys.exit(1)
    else:
        print("🟢 ALL TESTS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
