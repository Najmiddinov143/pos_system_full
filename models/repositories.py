# models/repositories.py - HTTP CLIENT VERSION (replaces SQLite)

import os
from datetime import datetime, timedelta
from models.api_client import api


# ============================================================
# USER REPOSITORY
# ============================================================
class UserRepository:
    def __init__(self):
        pass

    def authenticate(self, username, password):
        result = api.login(username, password)
        if result:
            from models.models import User
            return User(
                id=result["id"],
                username=result["username"],
                role=result["role"],
            )
        return None

    def get_all_users(self):
        return api.get("/auth/users") or []

    def create_user(self, username, password, role):
        return api.post(
            "/auth/users",
            {"username": username, "password": password, "role": role},
        )

    def change_password(self, old_password, new_password):
        """Change the current user's password via the API."""
        return api.post(
            "/auth/change-password",
            {"old_password": old_password, "new_password": new_password},
        )


# ============================================================
# PRODUCT REPOSITORY
# ============================================================
class ProductRepository:
    def __init__(self):
        pass

    def get_all(self):
        return api.get("/products/") or []

    def get_all_products(self):
        return self.get_all()

    def get_by_id(self, product_id):
        return api.get(f"/products/{product_id}")

    def get_product_by_id(self, product_id):
        return self.get_by_id(product_id)

    def get_product_by_name(self, name):
        return api.get(f"/products/search/{name}") or []

    def create(self, product):
        data = {}
        if hasattr(product, "__dict__"):
            for k in [
                "name", "category", "cost_price", "sell_price", "quantity",
                "unit", "min_quantity", "note", "image_path", "barcode",
                "supplier", "dollar_cost", "dollar_price", "exchange_rate",
                "category_id",
            ]:
                data[k] = getattr(product, k, 0 if "price" in k or "cost" in k or "quantity" in k else "")
        else:
            data = {k: product.get(k, 0 if "price" in k or "cost" in k or "quantity" in k else "")
                    for k in [
                        "name", "category", "cost_price", "sell_price", "quantity",
                        "unit", "min_quantity", "note", "image_path", "barcode",
                        "supplier", "dollar_cost", "dollar_price", "exchange_rate",
                        "category_id",
                    ]}
        result = api.post("/products/", data)
        if result and "id" in result:
            return self.get_by_id(result["id"])
        return result

    def update(self, product):
        data = {}
        if hasattr(product, "__dict__"):
            for k in [
                "name", "category", "cost_price", "sell_price", "quantity",
                "unit", "min_quantity", "note", "image_path", "barcode",
                "supplier", "dollar_cost", "dollar_price", "exchange_rate",
                "category_id",
            ]:
                data[k] = getattr(product, k, 0 if "price" in k or "cost" in k or "quantity" in k else "")
        else:
            data = {k: product.get(k, 0 if "price" in k or "cost" in k or "quantity" in k else "")
                    for k in [
                        "name", "category", "cost_price", "sell_price", "quantity",
                        "unit", "min_quantity", "note", "image_path", "barcode",
                        "supplier", "dollar_cost", "dollar_price", "exchange_rate",
                        "category_id",
                    ]}
        product_id = product.id if hasattr(product, "id") else product.get("id", 0)
        return api.put(f"/products/{product_id}", data)

    def delete(self, product_id):
        return api.delete(f"/products/{product_id}")

    def restore(self, product_id):
        return api.post(f"/products/{product_id}/restore")

    def update_stock(self, product_id, quantity_change):
        return api.put(f"/products/{product_id}/stock", None, {"quantity_change": quantity_change})


# ============================================================
# PURCHASE REPOSITORY
# ============================================================
class PurchaseRepository:
    def __init__(self):
        pass

    def create_purchase(self, purchase_data):
        result = api.post("/purchases/", purchase_data)
        return result.get("id") if result and "id" in result else None

    def get_all_purchases(self, product_id=None):
        params = {}
        if product_id:
            params["product_id"] = product_id
        return api.get("/purchases/", params=params) or []

    def get_purchase_by_id(self, purchase_id):
        return api.get(f"/purchases/{purchase_id}")

    def update_payment_status(self, purchase_id, is_paid):
        return api.put(f"/purchases/{purchase_id}", {"is_paid": 1 if is_paid else 0})

    def update_purchase(self, purchase_id, update_data):
        allowed = ["payment_type", "is_paid", "paid_date"]
        filtered = {k: v for k, v in update_data.items() if k in allowed}
        return api.put(f"/purchases/{purchase_id}", filtered)

    def delete_purchase(self, purchase_id):
        return api.delete(f"/purchases/{purchase_id}")

    def get_total_debt(self):
        result = api.get("/purchases/total-debt")
        return result.get("total_debt", 0.0) if result else 0.0

    def get_total_debt_usd(self):
        result = api.get("/purchases/total-debt-usd")
        return result.get("total_debt_usd", 0.0) if result else 0.0

    def get_purchases_by_date(self, start_date, end_date):
        purchases = api.get("/purchases/") or []
        filtered = []
        for p in purchases:
            pd = p.get("purchase_date", "")
            if pd and start_date <= pd[:10] <= end_date:
                filtered.append(p)
        return filtered

    def get_all_purchases_with_debts(self):
        return api.get("/purchases/debts") or []

    def get_debt_notifications(self, days=7):
        return api.get(f"/purchases/debts/notifications?days={days}") or []

    def get_debts_by_due_date(self, due_date):
        debts = self.get_all_purchases_with_debts()
        return [d for d in debts if d.get("due_date", "")[:10] == due_date[:10]]

    def _ensure_debt_payments_table(self, cursor=None):
        pass

    def mark_as_partially_paid(self, purchase_id, paid_amount, paid_date, cash_amount=0, card_amount=0):
        result = api.post(f"/purchases/{purchase_id}/pay", {
            "paid_amount": paid_amount,
            "paid_date": paid_date,
            "cash_amount": cash_amount,
            "card_amount": card_amount,
        })
        if result and result.get("success"):
            return result
        return {
            "success": False,
            "message": result.get("detail", "Payment failed") if result else "Connection error",
        }

    def get_payment_history(self, purchase_id):
        return api.get(f"/purchases/{purchase_id}/payments") or []

    def get_all_payment_history(self, start_date=None, end_date=None):
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return api.get("/purchases/payments/all", params=params) or []

    def mark_as_paid_with_date(self, purchase_id, paid_date):
        purchase = self.get_purchase_by_id(purchase_id)
        if not purchase:
            return {"success": False, "message": "Qarz topilmadi!"}
        debt_amount = float(purchase.get("total_cost", 0))
        result = self.mark_as_partially_paid(
            purchase_id, debt_amount, paid_date, cash_amount=debt_amount, card_amount=0
        )
        if result.get("success"):
            from controllers.sale_controller import SaleController
            sale_controller = SaleController()
            sales = sale_controller.get_sales_by_date(paid_date)
            if sales:
                sale_id = sales[0]["id"]
                current_total = sales[0]["total_amount"]
                new_total = max(0, current_total - debt_amount)
                sale_controller.update_sale_amount(sale_id, new_total)
        return result


# ============================================================
# SALE REPOSITORY
# ============================================================
class SaleRepository:
    def __init__(self):
        pass

    def get_all(self):
        return api.get("/sales/") or []

    def get_sales_with_items(self, start_date=None, end_date=None):
        params = {}
        if start_date and end_date:
            params["start_date"] = start_date
            params["end_date"] = end_date
        sales_data = api.get("/sales/", params=params) or []
        from models.models import Sale, SaleItem
        sales = []
        for s in sales_data:
            items = []
            for item in s.get("items", []):
                items.append(SaleItem(
                    id=item.get("id"), sale_id=item.get("sale_id"),
                    product_id=item.get("product_id"), quantity=item.get("quantity", 0),
                    sell_price=item.get("sell_price", 0), cost_price=item.get("cost_price", 0),
                    subtotal=item.get("subtotal", 0), product_name=item.get("product_name", ""),
                ))
            created_at = s.get("created_at", "")
            if created_at and isinstance(created_at, str):
                try:
                    created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                except:
                    created_at = datetime.now()
            sale = Sale(
                id=s.get("id"), total_amount=s.get("total_amount", 0),
                total_profit=s.get("total_profit", 0), discount=s.get("discount", 0),
                created_at=created_at, user_id=s.get("user_id"),
                car_number=s.get("car_number", ""), car_model=s.get("car_model", ""),
                phone_number=s.get("phone_number", ""),
                current_km=s.get("current_km", 0), next_km=s.get("next_km", 0),
                oil_change_date=s.get("oil_change_date", ""),
                next_oil_change_date=s.get("next_oil_change_date", ""),
                notification_date=s.get("notification_date", ""),
                is_notified=s.get("is_notified", 0),
                payment_type=s.get("payment_type", "Naxt"),
                bonus_amount=s.get("bonus_amount", 0),
                discount_amount=s.get("discount_amount", 0),
                cash_amount=s.get("cash_amount", 0), card_amount=s.get("card_amount", 0),
                extra_charge=s.get("extra_charge", 0),
                is_debt=s.get("is_debt", 0), debt_paid=s.get("debt_paid", 0),
                customer_name=s.get("customer_name", ""),
                customer_phone=s.get("customer_phone", ""),
                items=items,
            )
            sales.append(sale)
        return sales

    def create_sale(self, sale, items):
        sale_dict = {
            "total_amount": sale.total_amount, "total_profit": sale.total_profit,
            "discount": getattr(sale, "discount", 0),
            "discount_amount": getattr(sale, "discount_amount", 0),
            "user_id": sale.user_id,
            "car_number": getattr(sale, "car_number", ""),
            "car_model": getattr(sale, "car_model", ""),
            "phone_number": getattr(sale, "phone_number", ""),
            "current_km": getattr(sale, "current_km", 0),
            "next_km": getattr(sale, "next_km", 0),
            "oil_change_date": getattr(sale, "oil_change_date", ""),
            "next_oil_change_date": getattr(sale, "next_oil_change_date", ""),
            "notification_date": getattr(sale, "notification_date", ""),
            "is_notified": getattr(sale, "is_notified", 0),
            "payment_type": getattr(sale, "payment_type", "Naxt"),
            "bonus_amount": getattr(sale, "bonus_amount", 0),
            "cash_amount": getattr(sale, "cash_amount", 0),
            "card_amount": getattr(sale, "card_amount", 0),
            "extra_charge": getattr(sale, "extra_charge", 0),
            "is_debt": getattr(sale, "is_debt", 0),
            "debt_paid": getattr(sale, "debt_paid", 0),
            "customer_name": getattr(sale, "customer_name", ""),
            "customer_phone": getattr(sale, "customer_phone", ""),
            "items": [
                {"product_id": item.product_id, "quantity": item.quantity,
                 "sell_price": item.sell_price, "cost_price": item.cost_price,
                 "subtotal": item.subtotal}
                for item in items
            ],
        }
        result = api.post("/sales/", sale_dict)
        if result and "id" in result:
            return result["id"]
        return None

    def get_total_sales(self, start_date=None, end_date=None):
        if start_date and end_date:
            result = api.get(f"/sales/totals/{start_date}")
            return result.get("total", 0.0) if result else 0.0
        sales = self.get_all()
        return sum(float(s.get("total_amount", 0)) for s in sales)

    def get_total_profit(self, start_date=None, end_date=None):
        if start_date and end_date:
            result = api.get(f"/sales/totals/{start_date}")
            return result.get("profit", 0.0) if result else 0.0
        sales = self.get_all()
        total = 0
        for s in sales:
            if not (s.get("payment_type") == "Nasiya" and s.get("debt_paid", 0) == 0):
                total += float(s.get("total_profit", 0))
        return total

    def get_upcoming_notifications(self, days=3):
        sales_data = api.get(f"/sales/upcoming-notifications?days={days}") or []
        from models.models import Sale, SaleItem
        sales = []
        for s in sales_data:
            items = [SaleItem(
                id=item.get("id"), sale_id=item.get("sale_id"),
                product_id=item.get("product_id"), quantity=item.get("quantity", 0),
                sell_price=item.get("sell_price", 0), cost_price=item.get("cost_price", 0),
                subtotal=item.get("subtotal", 0), product_name=item.get("product_name", ""),
            ) for item in s.get("items", [])]
            created_at = s.get("created_at", "")
            if created_at and isinstance(created_at, str):
                try:
                    created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                except:
                    created_at = datetime.now()
            sale = Sale(
                id=s.get("id"), total_amount=s.get("total_amount", 0),
                total_profit=s.get("total_profit", 0), discount=s.get("discount", 0),
                created_at=created_at, user_id=s.get("user_id"),
                car_number=s.get("car_number", ""), car_model=s.get("car_model", ""),
                phone_number=s.get("phone_number", ""),
                current_km=s.get("current_km", 0), next_km=s.get("next_km", 0),
                oil_change_date=s.get("oil_change_date", ""),
                next_oil_change_date=s.get("next_oil_change_date", ""),
                notification_date=s.get("notification_date", ""),
                is_notified=s.get("is_notified", 0),
                payment_type=s.get("payment_type", "Naxt"),
                bonus_amount=s.get("bonus_amount", 0),
                discount_amount=s.get("discount_amount", 0),
                cash_amount=s.get("cash_amount", 0), card_amount=s.get("card_amount", 0),
                extra_charge=s.get("extra_charge", 0),
                is_debt=s.get("is_debt", 0), debt_paid=s.get("debt_paid", 0),
                customer_name=s.get("customer_name", ""),
                customer_phone=s.get("customer_phone", ""),
                items=items,
            )
            sales.append(sale)
        return sales

    def mark_as_notified(self, sale_id):
        return api.put(f"/sales/{sale_id}/mark-notified")

    def update_payment_type(self, sale_id, new_payment_type, customer_name="", customer_phone=""):
        return api.put(f"/sales/{sale_id}/payment-type", None, {
            "new_payment_type": new_payment_type,
            "customer_name": customer_name, "customer_phone": customer_phone,
        })

    def update_sale(self, sale_id, update_data):
        return api.put(f"/sales/{sale_id}", update_data)

    def get_sales_by_date(self, date_str):
        return api.get(f"/sales/date/{date_str}") or []

    def update_sale_amount(self, sale_id, new_amount):
        return api.put(f"/sales/{sale_id}", {"total_amount": new_amount})

    def get_cash_card_balance(self, date_str):
        result = api.get(f"/sales/cash-card-balance/{date_str}")
        if result:
            return {k: result.get(k, 0) for k in ["total_cash", "total_card", "available_cash", "available_card"]}
        return {"total_cash": 0, "total_card": 0, "available_cash": 0, "available_card": 0}

    def reduce_sale_by_payment(self, sale_id, total_delta, cash_delta, card_delta):
        return api.put(f"/sales/{sale_id}/reduce-by-payment", None, {
            "total_delta": total_delta, "cash_delta": cash_delta, "card_delta": card_delta,
        })


# ============================================================
# EXPENSE REPOSITORY
# ============================================================
class ExpenseRepository:
    def __init__(self):
        pass

    def get_all(self, start_date=None, end_date=None):
        params = {}
        if start_date and end_date:
            params["start_date"] = start_date
            params["end_date"] = end_date
        return api.get("/expenses/", params=params) or []

    def get_all_expenses(self, start_date=None, end_date=None):
        return self.get_all(start_date, end_date)

    def get_total(self, start_date=None, end_date=None):
        params = {}
        if start_date and end_date:
            params["start_date"] = start_date
            params["end_date"] = end_date
        result = api.get("/expenses/total", params=params)
        return result.get("total", 0.0) if result else 0.0

    def get_total_expenses(self, start_date=None, end_date=None):
        return self.get_total(start_date, end_date)

    def create_expense(self, expense):
        data = {
            "name": expense.name, "amount": expense.amount,
            "category": expense.category, "description": expense.description,
            "payment_type": getattr(expense, "payment_type", "Naxt") or "Naxt",
            "user_id": expense.user_id,
        }
        return api.post("/expenses/", data)

    def delete_expense(self, expense_id):
        return api.delete(f"/expenses/{expense_id}")

    def get_expenses_by_category(self, start_date=None, end_date=None):
        params = {}
        if start_date and end_date:
            params["start_date"] = start_date
            params["end_date"] = end_date
        return api.get("/expenses/by-category", params=params) or []


# ============================================================
# EMPLOYEE REPOSITORY
# ============================================================
class EmployeeRepository:
    def __init__(self):
        pass

    def get_all_employees(self):
        return api.get("/employees/") or []

    def get_employee_by_id(self, employee_id):
        return api.get(f"/employees/{employee_id}")

    def create_employee(self, employee):
        data = {"full_name": employee.full_name, "phone": employee.phone,
                "position": employee.position, "salary": employee.salary,
                "hire_date": employee.hire_date}
        return api.post("/employees/", data)

    def update_employee(self, employee):
        data = {"full_name": employee.full_name, "phone": employee.phone,
                "position": employee.position, "salary": employee.salary,
                "hire_date": employee.hire_date, "is_active": employee.is_active}
        return api.put(f"/employees/{employee.id}", data)

    def delete_employee(self, employee_id):
        return api.delete(f"/employees/{employee_id}")

    def get_attendance(self, employee_id, date):
        return api.get(f"/employees/{employee_id}/attendance/{date}")

    def check_in(self, employee_id, date, time):
        return api.post(f"/employees/{employee_id}/check-in", None, {"date": date, "time": time})

    def check_out(self, employee_id, date, time):
        return api.post(f"/employees/{employee_id}/check-out", None, {"date": date, "time": time})


# ============================================================
# BACKUP REPOSITORY
# ============================================================
class BackupRepository:
    def __init__(self):
        pass

    def save_backup_record(self, backup):
        data = {
            "backup_date": backup.backup_date,
            "file_name": backup.file_name,
            "file_size": backup.file_size,
            "created_by": backup.created_by,
        }
        return api.post("/backup/", data)

    def get_backup_history(self, limit=20):
        return api.get(f"/backup/history?limit={limit}") or []

    def delete_backup_record(self, backup_id):
        return api.delete(f"/backup/{backup_id}")

    def create_dump(self):
        """Run pg_dump on the server and return the record."""
        return api.post("/backup/create")

    def download_dump(self, file_name, save_to):
        """Download a dump file from the server and save it locally."""
        import requests as _requests
        try:
            url = f"{api.session.headers.get('X-API-Key', '')}"
            # Use the underlying session directly for binary download
            base = api.get.__func__  # we need the base URL
        except Exception:
            pass

        # Build the full URL manually since api.get returns JSON only
        from models.api_client import API_BASE_URL
        headers = {"X-API-Key": api._api_key or ""}
        resp = _requests.get(
            f"{API_BASE_URL}/backup/download/{file_name}",
            headers=headers, timeout=60, stream=True,
        )
        if resp.status_code == 200:
            with open(save_to, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        return False

    def restore_dump(self, file_path):
        """Upload a SQL dump file to the server for database restore."""
        import requests as _requests
        from models.api_client import API_BASE_URL
        headers = {"X-API-Key": api._api_key or ""}
        with open(file_path, "rb") as f:
            resp = _requests.post(
                f"{API_BASE_URL}/backup/restore",
                headers=headers,
                files={"file": (os.path.basename(file_path), f, "application/sql")},
                timeout=120,
            )
        if resp.status_code == 200:
            return resp.json()
        return None


# ============================================================
# NOTIFICATION REPOSITORY
# ============================================================
class NotificationRepository:
    def __init__(self):
        pass

    def get_all_notifications(self, user_id=None):
        params = {}
        if user_id:
            params["user_id"] = user_id
        return api.get("/notifications/", params=params) or []

    def create_notification(self, notification):
        if isinstance(notification, dict):
            data = {"title": notification.get("title", ""), "message": notification.get("message", ""),
                    "type": notification.get("type", "Eslatma"), "user_id": notification.get("user_id")}
        else:
            data = {"title": getattr(notification, "title", ""), "message": getattr(notification, "message", ""),
                    "type": getattr(notification, "type", "Eslatma"), "user_id": getattr(notification, "user_id", None)}
        return api.post("/notifications/", data)

    def mark_as_read(self, notification_id):
        return api.put(f"/notifications/{notification_id}/read")

    def mark_all_as_read(self, user_id=None):
        params = {}
        if user_id:
            params["user_id"] = user_id
        return api.put("/notifications/read-all", None, params)

    def get_unread_count(self, user_id=None):
        params = {}
        if user_id:
            params["user_id"] = user_id
        result = api.get("/notifications/unread-count", params=params)
        return result.get("count", 0) if result else 0

    def delete_notification(self, notification_id):
        return api.delete(f"/notifications/{notification_id}")

    def delete_all_notifications(self, user_id=None):
        return api.delete("/notifications/")

    def get_notification_by_id(self, notification_id):
        all_notifs = self.get_all_notifications()
        for n in all_notifs:
            if n.get("id") == notification_id:
                return n
        return None


# ============================================================
# SHOP SETTINGS REPOSITORY
# ============================================================
class ShopSettingsRepository:
    def __init__(self):
        pass

    def get_settings(self):
        return api.get("/settings/shop")

    def update_settings(self, settings):
        if isinstance(settings, dict):
            data = {k: settings.get(k, "") for k in ["shop_name", "address", "phone", "logo_path", "receipt_footer"]}
        else:
            data = {k: getattr(settings, k, "") for k in ["shop_name", "address", "phone", "logo_path", "receipt_footer"]}
        return api.put("/settings/shop", data)


# ============================================================
# SETTING REPOSITORY (key-value)
# ============================================================
class SettingRepository:
    def __init__(self):
        pass

    def get(self, key):
        result = api.get(f"/settings/{key}")
        return result.get("value") if result else None

    def set(self, key, value):
        return api.put(f"/settings/{key}", {"value": str(value)})

    def get_all(self):
        return []


# ============================================================
# INCOME REPOSITORY
# ============================================================
class IncomeRepository:
    def __init__(self):
        pass

    def create_income(self, amount, note="", user_id=None):
        result = api.post("/incomes/", {"amount": amount, "note": note, "user_id": user_id})
        return result.get("id") if result and "id" in result else None

    def get_by_date(self, date_str):
        return api.get("/incomes/", params={"date": date_str}) or []

    def get_by_date_range(self, start_date, end_date):
        return api.get("/incomes/") or []

    def delete(self, income_id):
        return api.delete(f"/incomes/{income_id}")


# ============================================================
# FIRM REPOSITORY
# ============================================================
class FirmRepository:
    def __init__(self):
        pass

    def get_all(self):
        return api.get("/firms/") or []

    def get_by_id(self, firm_id):
        return api.get(f"/firms/{firm_id}")

    def get_by_name(self, name):
        return api.get(f"/firms/search/{name}") or []

    def create(self, firm_data):
        result = api.post("/firms/", firm_data)
        return result.get("id") if result and "id" in result else None

    def update(self, firm_data):
        firm_id = firm_data.get("id", 0)
        return api.put(f"/firms/{firm_id}", firm_data)

    def delete(self, firm_id):
        return api.delete(f"/firms/{firm_id}")

    def add_debt(self, firm_id, amount):
        firm = self.get_by_id(firm_id)
        if firm:
            new_debt = float(firm.get("total_debt", 0)) + amount
            return api.put(f"/firms/{firm_id}", {"total_debt": new_debt})
        return False

    def reduce_debt(self, firm_id, amount):
        firm = self.get_by_id(firm_id)
        if firm:
            new_debt = max(0, float(firm.get("total_debt", 0)) - amount)
            return api.put(f"/firms/{firm_id}", {"total_debt": new_debt})
        return False

    def get_total_debt(self):
        result = api.get("/firms/total-debt/all")
        return result.get("total_debt", 0.0) if result else 0.0


# ============================================================
# FIRM DEBT REPOSITORY
# ============================================================
class FirmDebtRepository:
    def __init__(self):
        pass

    def _ensure_payments_table(self, cursor=None):
        pass

    def create(self, firm_id, amount, description="", debt_type="qarz", firm_name=""):
        data = {"firm_id": firm_id, "amount": amount, "description": description,
                "debt_type": debt_type, "firm_name": firm_name}
        result = api.post("/firms/debts", data)
        return result.get("id") if result and "id" in result else None

    def get_by_firm(self, firm_id):
        return api.get(f"/firms/debts/{firm_id}") or []

    def get_all(self):
        return api.get("/firms/debts/all/list") or []

    def get_total_debt(self, firm_id):
        debts = self.get_by_firm(firm_id)
        total = 0
        for d in debts:
            amt = float(d.get("amount", 0))
            total += amt if d.get("debt_type") == "qarz" else -amt
        return total

    def delete(self, debt_id):
        return False

    def get_debt_by_id(self, debt_id):
        for d in self.get_all():
            if d.get("id") == debt_id:
                return d
        return None

    def pay_debt(self, debt_id, paid_amount, paid_date=None, cash_amount=0, card_amount=0):
        data = {"paid_amount": paid_amount,
                "paid_date": paid_date or datetime.now().strftime("%Y-%m-%d"),
                "cash_amount": cash_amount, "card_amount": card_amount}
        result = api.post(f"/firms/debts/{debt_id}/pay", data)
        if result and result.get("success"):
            return result
        return {"success": False, "message": result.get("detail", "Failed") if result else "Connection error"}

    def get_payment_history(self, debt_id):
        return api.get(f"/firms/debts/{debt_id}/payments") or []

    def get_all_payment_history(self, start_date=None, end_date=None):
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return api.get("/firms/payments/all/history", params=params) or []

    def get_payment_summary(self, firm_id=None, start_date=None, end_date=None):
        params = {}
        if firm_id:
            params["firm_id"] = firm_id
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        result = api.get("/firms/payments/summary", params=params)
        return result or {"total_cash": 0, "total_card": 0, "total_paid": 0, "payment_count": 0}


# ============================================================
# CATEGORY REPOSITORY
# ============================================================
class CategoryRepository:
    def __init__(self):
        pass

    def get_all(self):
        return api.get("/categories/") or []

    def get_by_id(self, category_id):
        return api.get(f"/categories/{category_id}")

    def create(self, name, parent_id=None, icon=None, color=None):
        result = api.post("/categories/", {"name": name, "parent_id": parent_id, "icon": icon, "color": color})
        return result.get("id") if result and "id" in result else None

    def update(self, category_id, name, parent_id=None, icon=None, color=None):
        return api.put(f"/categories/{category_id}", {"name": name, "parent_id": parent_id, "icon": icon, "color": color})

    def delete(self, category_id):
        return api.delete(f"/categories/{category_id}")

    def get_products_by_category(self, category_id):
        if category_id is None:
            return []
        return api.get(f"/categories/{category_id}/products") or []

    def assign_products(self, product_ids, category_id):
        return api.post(f"/categories/{category_id}/assign-products", product_ids)

    def get_parent_categories(self):
        return [c for c in self.get_all() if c.get("parent_id") is None]

    def get_subcategories(self, parent_id):
        return [c for c in self.get_all() if c.get("parent_id") == parent_id]

    def get_category_tree(self):
        return api.get("/categories/tree") or []

    def get_category_count(self):
        return len(self.get_all())
