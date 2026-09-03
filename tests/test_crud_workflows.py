#!/usr/bin/env python3
"""
End-to-end workflow tests for the POS System API.

Tests full CRUD lifecycle for products, sales, purchases, and expenses.
Each workflow: CREATE → READ → UPDATE → verify → DELETE → verify gone.

Requires the backend to be running (docker compose up).
"""

import sys
import time
import requests
from datetime import datetime, date

BASE_URL = "http://localhost:8000"
API_KEY = None
CREATED_IDS = {"products": [], "sales": [], "purchases": [], "expenses": []}

PASS = 0
FAIL = 0


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


def auth_headers():
    return {"X-API-Key": API_KEY}


def setup_login():
    """Login as admin and store API key."""
    global API_KEY
    print("\n🔑 Logging in as admin...")
    r = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "admin", "password": "admin123"
    }, timeout=10)
    if r.status_code != 200:
        print(f"❌ Login failed: {r.status_code} {r.text}")
        sys.exit(1)
    API_KEY = r.json()["api_key"]
    log_pass(f"Logged in (user_id={r.json()['id']}, role={r.json()['role']})")


# ════════════════════════════════════════════════════════════════
#  PRODUCTS WORKFLOW
# ════════════════════════════════════════════════════════════════

def test_products_workflow():
    print("\n" + "=" * 60)
    print("📦  PRODUCTS WORKFLOW")
    print("=" * 60)

    # --- CREATE ---
    payload = {
        "name": "TEST_WIDGET_001",
        "category": "Test",
        "cost_price": 10.50,
        "sell_price": 25.00,
        "quantity": 100,
        "unit": "dona",
        "min_quantity": 5,
        "barcode": "TEST001",
        "supplier": "Test Supplier Inc.",
    }
    r = requests.post(f"{BASE_URL}/api/products/", json=payload, headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        pid = r.json()["id"]
        CREATED_IDS["products"].append(pid)
        log_pass(f"POST /api/products/ → created id={pid}")
    else:
        log_fail(f"POST /api/products/ → {r.status_code}", r.text[:300])
        return

    # --- READ by ID ---
    r = requests.get(f"{BASE_URL}/api/products/{pid}", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        data = r.json()
        checks = [
            ("name", data["name"], "TEST_WIDGET_001"),
            ("cost_price", data["cost_price"], 10.50),
            ("sell_price", data["sell_price"], 25.00),
            ("quantity", data["quantity"], 100),
            ("barcode", data["barcode"], "TEST001"),
        ]
        all_ok = True
        for field, got, expected in checks:
            if got != expected:
                log_fail(f"GET /api/products/{pid} field '{field}': got {got!r}, expected {expected!r}")
                all_ok = False
        if all_ok:
            log_pass(f"GET /api/products/{pid} → all fields match")
    else:
        log_fail(f"GET /api/products/{pid} → {r.status_code}", r.text[:300])
        return

    # --- appears in LIST ---
    r = requests.get(f"{BASE_URL}/api/products/", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        ids = [p["id"] for p in r.json()]
        if pid in ids:
            log_pass(f"GET /api/products/ → test product appears in list")
        else:
            log_fail(f"GET /api/products/ → test product NOT in list (got {len(ids)} products)")
    else:
        log_fail(f"GET /api/products/ → {r.status_code}")

    # --- SEARCH ---
    r = requests.get(f"{BASE_URL}/api/products/search/TEST_WIDGET", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        results = r.json()
        if any(p["id"] == pid for p in results):
            log_pass(f"GET /api/products/search/TEST_WIDGET → found")
        else:
            log_fail(f"GET /api/products/search/TEST_WIDGET → not found in {len(results)} results")
    else:
        log_fail(f"GET /api/products/search/TEST_WIDGET → {r.status_code}")

    # --- UPDATE ---
    update_payload = {"sell_price": 30.00, "name": "TEST_WIDGET_001_V2"}
    r = requests.put(f"{BASE_URL}/api/products/{pid}", json=update_payload, headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        data = r.json()
        if data["sell_price"] == 30.00 and data["name"] == "TEST_WIDGET_001_V2":
            log_pass(f"PUT /api/products/{pid} → name and sell_price updated")
        else:
            log_fail(f"PUT /api/products/{pid} → fields not updated", str(data)[:200])
    else:
        log_fail(f"PUT /api/products/{pid} → {r.status_code}", r.text[:300])

    # --- verify update persisted ---
    r = requests.get(f"{BASE_URL}/api/products/{pid}", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        data = r.json()
        if data["name"] == "TEST_WIDGET_001_V2" and data["sell_price"] == 30.00:
            log_pass(f"GET after update → verified persisted")
        else:
            log_fail(f"GET after update → values not persisted", str(data)[:200])

    # --- DELETE (soft) ---
    r = requests.delete(f"{BASE_URL}/api/products/{pid}", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        log_pass(f"DELETE /api/products/{pid} → soft-deleted")
    else:
        log_fail(f"DELETE /api/products/{pid} → {r.status_code}", r.text[:300])

    # --- verify gone from active list ---
    r = requests.get(f"{BASE_URL}/api/products/", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        ids = [p["id"] for p in r.json()]
        if pid not in ids:
            log_pass(f"GET /api/products/ → soft-deleted product no longer in active list")
        else:
            log_fail(f"GET /api/products/ → soft-deleted product STILL in active list")

    # --- restore ---
    r = requests.post(f"{BASE_URL}/api/products/{pid}/restore", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        log_pass(f"POST /api/products/{pid}/restore → restored")
    else:
        log_fail(f"POST /api/products/{pid}/restore → {r.status_code}", r.text[:300])

    # --- verify restored ---
    r = requests.get(f"{BASE_URL}/api/products/{pid}", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        log_pass(f"GET /api/products/{pid} after restore → exists again")
    else:
        log_fail(f"GET /api/products/{pid} after restore → {r.status_code}")


# ════════════════════════════════════════════════════════════════
#  SALES WORKFLOW (requires a product with stock)
# ════════════════════════════════════════════════════════════════

def test_sales_workflow():
    print("\n" + "=" * 60)
    print("💰  SALES WORKFLOW")
    print("=" * 60)

    # --- Setup: create a product with stock ---
    payload = {
        "name": "TEST_SALE_ITEM_001",
        "category": "Test",
        "cost_price": 15.00,
        "sell_price": 40.00,
        "quantity": 50,
        "unit": "dona",
    }
    r = requests.post(f"{BASE_URL}/api/products/", json=payload, headers=auth_headers(), timeout=10)
    if r.status_code != 200:
        log_fail(f"Setup: create product failed → {r.status_code}", r.text[:200])
        return
    product_id = r.json()["id"]
    CREATED_IDS["products"].append(product_id)
    log_pass(f"Setup: created product id={product_id} (qty=50)")

    # --- CREATE SALE ---
    sale_payload = {
        "total_amount": 200.00,
        "total_profit": 125.00,
        "discount": 0,
        "payment_type": "Naxt",
        "cash_amount": 200.00,
        "card_amount": 0,
        "customer_name": "Test Customer",
        "customer_phone": "+998901234567",
        "car_number": "TEST123",
        "car_model": "Toyota Camry",
        "items": [
            {
                "product_id": product_id,
                "quantity": 5,
                "sell_price": 40.00,
                "cost_price": 15.00,
                "subtotal": 200.00,
            }
        ],
    }
    r = requests.post(f"{BASE_URL}/api/sales/", json=sale_payload, headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        sale_id = r.json()["id"]
        CREATED_IDS["sales"].append(sale_id)
        log_pass(f"POST /api/sales/ → created id={sale_id}")
    else:
        log_fail(f"POST /api/sales/ → {r.status_code}", r.text[:300])
        return

    # --- inventory deduction ---
    r = requests.get(f"{BASE_URL}/api/products/{product_id}", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        new_qty = r.json()["quantity"]
        if new_qty == 45:
            log_pass(f"Inventory deduction → qty dropped from 50 to {new_qty}")
        else:
            log_fail(f"Inventory deduction → expected 45, got {new_qty}")

    # --- READ sale by ID ---
    r = requests.get(f"{BASE_URL}/api/sales/{sale_id}", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        data = r.json()
        checks = [
            ("total_amount", data["total_amount"], 200.0),
            ("customer_name", data["customer_name"], "Test Customer"),
            ("car_number", data["car_number"], "TEST123"),
        ]
        all_ok = True
        for field, got, expected in checks:
            if got != expected:
                log_fail(f"GET /api/sales/{sale_id} field '{field}': got {got!r}, expected {expected!r}")
                all_ok = False
        # check items
        if "items" in data and len(data["items"]) == 1:
            item = data["items"][0]
            if item["product_id"] == product_id and item["quantity"] == 5:
                log_pass(f"GET /api/sales/{sale_id} → fields + items correct")
            else:
                log_fail(f"GET /api/sales/{sale_id} → item data mismatch", str(item)[:200])
        else:
            log_fail(f"GET /api/sales/{sale_id} → expected 1 item, got {len(data.get('items', []))}")
            all_ok = False
        if all_ok:
            pass  # already logged
    else:
        log_fail(f"GET /api/sales/{sale_id} → {r.status_code}", r.text[:300])

    # --- appears in LIST ---
    r = requests.get(f"{BASE_URL}/api/sales/", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        ids = [s["id"] for s in r.json()]
        if sale_id in ids:
            log_pass(f"GET /api/sales/ → test sale appears in list")
        else:
            log_fail(f"GET /api/sales/ → test sale NOT in list")
    else:
        log_fail(f"GET /api/sales/ → {r.status_code}")

    # --- DATE FILTER ---
    today = date.today().isoformat()
    r = requests.get(f"{BASE_URL}/api/sales/date/{today}", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        ids = [s["id"] for s in r.json()]
        if sale_id in ids:
            log_pass(f"GET /api/sales/date/{today} → found sale")
        else:
            log_fail(f"GET /api/sales/date/{today} → sale not found in {len(ids)} results")
    else:
        log_fail(f"GET /api/sales/date/{today} → {r.status_code}")

    # --- TOTALS ---
    r = requests.get(f"{BASE_URL}/api/sales/totals/{today}", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        data = r.json()
        total = data.get("total", 0)
        count = data.get("count", 0)
        if total > 0 and count > 0:
            log_pass(f"GET /api/sales/totals/{today} → total={total}, count={count}")
        else:
            log_fail(f"GET /api/sales/totals/{today} → total={total}, count={count} (expected > 0)")
    else:
        log_fail(f"GET /api/sales/totals/{today} → {r.status_code}")

    # --- UPDATE sale ---
    update_payload = {"customer_name": "Updated Customer", "car_model": "Honda Accord"}
    r = requests.put(f"{BASE_URL}/api/sales/{sale_id}", json=update_payload, headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        data = r.json()
        if data.get("customer_name") == "Updated Customer":
            log_pass(f"PUT /api/sales/{sale_id} → customer_name updated")
        else:
            log_fail(f"PUT /api/sales/{sale_id} → customer_name not updated", str(data)[:200])
    else:
        log_fail(f"PUT /api/sales/{sale_id} → {r.status_code}", r.text[:300])

    # --- verify update ---
    r = requests.get(f"{BASE_URL}/api/sales/{sale_id}", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        if r.json().get("customer_name") == "Updated Customer":
            log_pass(f"GET after update → persisted")
        else:
            log_fail(f"GET after update → not persisted")

    # --- CASH CARD BALANCE ---
    r = requests.get(f"{BASE_URL}/api/sales/cash-card-balance/{today}", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        data = r.json()
        if "total_cash" in data and "total_card" in data:
            log_pass(f"GET /api/sales/cash-card-balance → total_cash={data['total_cash']}")
        else:
            log_fail(f"GET /api/sales/cash-card-balance → missing fields", str(data)[:200])
    else:
        log_fail(f"GET /api/sales/cash-card-balance/{today} → {r.status_code}")


# ════════════════════════════════════════════════════════════════
#  PURCHASES WORKFLOW
# ════════════════════════════════════════════════════════════════

def test_purchases_workflow():
    print("\n" + "=" * 60)
    print("🛒  PURCHASES WORKFLOW")
    print("=" * 60)

    # --- Setup: create a product ---
    payload = {
        "name": "TEST_PURCHASE_ITEM_001",
        "category": "Test",
        "cost_price": 5.00,
        "sell_price": 12.00,
        "quantity": 0,
        "unit": "dona",
    }
    r = requests.post(f"{BASE_URL}/api/products/", json=payload, headers=auth_headers(), timeout=10)
    if r.status_code != 200:
        log_fail(f"Setup: create product failed → {r.status_code}", r.text[:200])
        return
    product_id = r.json()["id"]
    CREATED_IDS["products"].append(product_id)
    log_pass(f"Setup: created product id={product_id}")

    # --- CREATE PURCHASE (Naxt) ---
    purchase_payload = {
        "product_id": product_id,
        "product_name": "TEST_PURCHASE_ITEM_001",
        "quantity": 20,
        "unit_cost": 5.00,
        "total_cost": 100.00,
        "payment_type": "Naxt",
        "purchase_date": date.today().isoformat(),
    }
    r = requests.post(f"{BASE_URL}/api/purchases/", json=purchase_payload, headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        purchase_id = r.json()["id"]
        CREATED_IDS["purchases"].append(purchase_id)
        log_pass(f"POST /api/purchases/ → created id={purchase_id}")
    else:
        log_fail(f"POST /api/purchases/ → {r.status_code}", r.text[:300])
        return

    # --- READ by ID ---
    r = requests.get(f"{BASE_URL}/api/purchases/{purchase_id}", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        data = r.json()
        checks = [
            ("product_id", data["product_id"], product_id),
            ("quantity", data["quantity"], 20),
            ("total_cost", data["total_cost"], 100.0),
            ("payment_type", data["payment_type"], "Naxt"),
        ]
        all_ok = True
        for field, got, expected in checks:
            if got != expected:
                log_fail(f"GET /api/purchases/{purchase_id} field '{field}': got {got!r}, expected {expected!r}")
                all_ok = False
        if all_ok:
            log_pass(f"GET /api/purchases/{purchase_id} → all fields match")
    else:
        log_fail(f"GET /api/purchases/{purchase_id} → {r.status_code}", r.text[:300])
        return

    # --- appears in LIST ---
    r = requests.get(f"{BASE_URL}/api/purchases/", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        ids = [p["id"] for p in r.json()]
        if purchase_id in ids:
            log_pass(f"GET /api/purchases/ → test purchase appears in list")
        else:
            log_fail(f"GET /api/purchases/ → test purchase NOT in list")
    else:
        log_fail(f"GET /api/purchases/ → {r.status_code}")

    # --- filtered by product_id ---
    r = requests.get(f"{BASE_URL}/api/purchases/?product_id={product_id}", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        ids = [p["id"] for p in r.json()]
        if purchase_id in ids:
            log_pass(f"GET /api/purchases/?product_id={product_id} → found")
        else:
            log_fail(f"GET /api/purchases/?product_id={product_id} → not found")
    else:
        log_fail(f"GET /api/purchases/?product_id={product_id} → {r.status_code}")

    # --- UPDATE ---
    update_payload = {"payment_type": "Nasiya", "due_date": "2026-12-31"}
    r = requests.put(f"{BASE_URL}/api/purchases/{purchase_id}", json=update_payload, headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        data = r.json()
        if data.get("payment_type") == "Nasiya" and data.get("due_date") == "2026-12-31":
            log_pass(f"PUT /api/purchases/{purchase_id} → payment_type + due_date updated")
        else:
            log_fail(f"PUT /api/purchases/{purchase_id} → fields not updated", str(data)[:200])
    else:
        log_fail(f"PUT /api/purchases/{purchase_id} → {r.status_code}", r.text[:300])

    # --- verify update ---
    r = requests.get(f"{BASE_URL}/api/purchases/{purchase_id}", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        data = r.json()
        if data.get("payment_type") == "Nasiya":
            log_pass(f"GET after update → persisted (payment_type=Nasiya)")
        else:
            log_fail(f"GET after update → not persisted, got payment_type={data.get('payment_type')}")

    # --- DEBT ENDPOINTS (nasiya) ---
    r = requests.get(f"{BASE_URL}/api/purchases/debts", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        ids = [d["id"] for d in r.json()]
        if purchase_id in ids:
            log_pass(f"GET /api/purchases/debts → nasiya purchase appears")
        else:
            log_fail(f"GET /api/purchases/debts → nasiya purchase NOT found")
    else:
        log_fail(f"GET /api/purchases/debts → {r.status_code}")

    # --- PAYMENT on nasiya debt ---
    pay_payload = {
        "paid_amount": 50.00,
        "paid_date": date.today().isoformat(),
        "cash_amount": 50.00,
        "card_amount": 0,
    }
    r = requests.post(f"{BASE_URL}/api/purchases/{purchase_id}/pay", json=pay_payload, headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        data = r.json()
        if data.get("success") and data.get("remaining_debt") == 50.0:
            log_pass(f"POST /api/purchases/{purchase_id}/pay → paid 50, remaining=50")
        else:
            log_fail(f"POST /api/purchases/{purchase_id}/pay → unexpected result", str(data)[:200])
    else:
        log_fail(f"POST /api/purchases/{purchase_id}/pay → {r.status_code}", r.text[:300])

    # --- PAYMENT HISTORY ---
    r = requests.get(f"{BASE_URL}/api/purchases/{purchase_id}/payments", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        payments = r.json()
        if len(payments) == 1 and payments[0]["paid_amount"] == 50.0:
            log_pass(f"GET /api/purchases/{purchase_id}/payments → 1 payment of 50")
        else:
            log_fail(f"GET /api/purchases/{purchase_id}/payments → expected 1 payment of 50",
                     f"got {len(payments)} payments")
    else:
        log_fail(f"GET /api/purchases/{purchase_id}/payments → {r.status_code}")

    # --- FULL PAY remaining debt ---
    pay_payload2 = {
        "paid_amount": 50.00,
        "paid_date": date.today().isoformat(),
        "cash_amount": 30.00,
        "card_amount": 20.00,
    }
    r = requests.post(f"{BASE_URL}/api/purchases/{purchase_id}/pay", json=pay_payload2, headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        data = r.json()
        if data.get("success") and data.get("remaining_debt", 999) <= 0:
            log_pass(f"POST /api/purchases/{purchase_id}/pay → fully paid")
        else:
            log_fail(f"POST /api/purchases/{purchase_id}/pay → not fully paid", str(data)[:200])
    else:
        log_fail(f"POST /api/purchases/{purchase_id}/pay (2nd) → {r.status_code}", r.text[:300])

    # --- verify fully paid ---
    r = requests.get(f"{BASE_URL}/api/purchases/{purchase_id}", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        data = r.json()
        if data.get("is_paid") == 1:
            log_pass(f"GET after full payment → is_paid=1")
        else:
            log_fail(f"GET after full payment → is_paid={data.get('is_paid')} (expected 1)")

    # --- DELETE ---
    r = requests.delete(f"{BASE_URL}/api/purchases/{purchase_id}", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        log_pass(f"DELETE /api/purchases/{purchase_id} → deleted")
    else:
        log_fail(f"DELETE /api/purchases/{purchase_id} → {r.status_code}", r.text[:300])

    # --- verify gone ---
    r = requests.get(f"{BASE_URL}/api/purchases/{purchase_id}", headers=auth_headers(), timeout=10)
    if r.status_code == 404:
        log_pass(f"GET /api/purchases/{purchase_id} after delete → 404 confirmed")
    else:
        log_fail(f"GET /api/purchases/{purchase_id} after delete → expected 404, got {r.status_code}")

    # --- TOTAL DEBT ---
    r = requests.get(f"{BASE_URL}/api/purchases/total-debt", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        log_pass(f"GET /api/purchases/total-debt → returned {r.json()}")
    else:
        log_fail(f"GET /api/purchases/total-debt → {r.status_code}")

    r = requests.get(f"{BASE_URL}/api/purchases/total-debt-usd", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        log_pass(f"GET /api/purchases/total-debt-usd → returned {r.json()}")
    else:
        log_fail(f"GET /api/purchases/total-debt-usd → {r.status_code}")


# ════════════════════════════════════════════════════════════════
#  EXPENSES WORKFLOW
# ════════════════════════════════════════════════════════════════

def test_expenses_workflow():
    print("\n" + "=" * 60)
    print("🧾  EXPENSES WORKFLOW")
    print("=" * 60)

    # --- CREATE ---
    payload = {
        "name": "TEST_EXPENSE_001",
        "amount": 75.50,
        "category": "TestCategory",
        "description": "Automated test expense",
        "payment_type": "Naxt",
    }
    r = requests.post(f"{BASE_URL}/api/expenses/", json=payload, headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        log_pass(f"POST /api/expenses/ → created")
        # Expenses don't return the ID in the response, so we need to find it
    else:
        log_fail(f"POST /api/expenses/ → {r.status_code}", r.text[:300])
        return

    # --- appears in LIST ---
    r = requests.get(f"{BASE_URL}/api/expenses/", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        expenses = r.json()
        test_exp = [e for e in expenses if e["name"] == "TEST_EXPENSE_001"]
        if test_exp:
            exp_id = test_exp[0]["id"]
            CREATED_IDS["expenses"].append(exp_id)
            log_pass(f"GET /api/expenses/ → found test expense id={exp_id}")
        else:
            log_fail(f"GET /api/expenses/ → test expense NOT found")
            return
    else:
        log_fail(f"GET /api/expenses/ → {r.status_code}")
        return

    # --- verify fields ---
    exp = test_exp[0]
    checks = [
        ("name", exp["name"], "TEST_EXPENSE_001"),
        ("amount", float(exp["amount"]), 75.50),
        ("category", exp["category"], "TestCategory"),
        ("description", exp["description"], "Automated test expense"),
    ]
    all_ok = True
    for field, got, expected in checks:
        if got != expected:
            log_fail(f"Expense field '{field}': got {got!r}, expected {expected!r}")
            all_ok = False
    if all_ok:
        log_pass(f"All expense fields match")

    # --- TOTAL ---
    r = requests.get(f"{BASE_URL}/api/expenses/total", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        total = r.json().get("total", 0)
        if total > 0:
            log_pass(f"GET /api/expenses/total → {total}")
        else:
            log_fail(f"GET /api/expenses/total → {total} (expected > 0)")
    else:
        log_fail(f"GET /api/expenses/total → {r.status_code}")

    # --- BY CATEGORY ---
    r = requests.get(f"{BASE_URL}/api/expenses/by-category", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        cats = r.json()
        test_cat = [c for c in cats if c["category"] == "TestCategory"]
        if test_cat:
            log_pass(f"GET /api/expenses/by-category → TestCategory found (total={test_cat[0]['total']})")
        else:
            log_fail(f"GET /api/expenses/by-category → TestCategory not found")
    else:
        log_fail(f"GET /api/expenses/by-category → {r.status_code}")

    # --- DELETE ---
    r = requests.delete(f"{BASE_URL}/api/expenses/{exp_id}", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        log_pass(f"DELETE /api/expenses/{exp_id} → deleted")
    else:
        log_fail(f"DELETE /api/expenses/{exp_id} → {r.status_code}", r.text[:300])

    # --- verify gone ---
    r = requests.get(f"{BASE_URL}/api/expenses/", headers=auth_headers(), timeout=10)
    if r.status_code == 200:
        ids = [e["id"] for e in r.json()]
        if exp_id not in ids:
            log_pass(f"GET /api/expenses/ → deleted expense no longer in list")
        else:
            log_fail(f"GET /api/expenses/ → deleted expense STILL in list")


# ════════════════════════════════════════════════════════════════
#  CLEANUP
# ════════════════════════════════════════════════════════════════

def cleanup():
    print("\n" + "=" * 60)
    print("🧹  CLEANUP")
    print("=" * 60)

    # Delete expenses
    for eid in CREATED_IDS["expenses"]:
        r = requests.delete(f"{BASE_URL}/api/expenses/{eid}", headers=auth_headers(), timeout=10)
        if r.status_code == 200:
            log_pass(f"Cleanup: deleted expense {eid}")
        else:
            print(f"  ⚠️  Could not delete expense {eid}: {r.status_code}")

    # Delete purchases
    for pid in CREATED_IDS["purchases"]:
        r = requests.delete(f"{BASE_URL}/api/purchases/{pid}", headers=auth_headers(), timeout=10)
        if r.status_code == 200:
            log_pass(f"Cleanup: deleted purchase {pid}")
        else:
            print(f"  ⚠️  Could not delete purchase {pid}: {r.status_code}")

    # Soft-delete products
    for pid in CREATED_IDS["products"]:
        r = requests.delete(f"{BASE_URL}/api/products/{pid}", headers=auth_headers(), timeout=10)
        if r.status_code == 200:
            log_pass(f"Cleanup: soft-deleted product {pid}")
        else:
            print(f"  ⚠️  Could not delete product {pid}: {r.status_code}")

    # Note: sales can't be deleted via API, but they're test data only
    if CREATED_IDS["sales"]:
        print(f"  ℹ️  {len(CREATED_IDS['sales'])} test sale(s) left (no DELETE endpoint for sales)")


# ════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("🧪  POS SYSTEM — END-TO-END WORKFLOW TESTS")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Time:   {datetime.now().isoformat()}")

    # Check server is up
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if r.status_code != 200:
            print(f"❌ Server not healthy: {r.status_code}")
            sys.exit(1)
        print(f"✅ Server is healthy")
    except requests.ConnectionError:
        print(f"❌ Cannot connect to {BASE_URL} — is docker compose up?")
        sys.exit(1)

    setup_login()

    test_products_workflow()
    test_sales_workflow()
    test_purchases_workflow()
    test_expenses_workflow()
    cleanup()

    # Summary
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
