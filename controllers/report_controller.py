# controllers/report_controller.py - UPDATED to use API
from models.repositories import ProductRepository, SaleRepository, ExpenseRepository
from models.api_client import api
from datetime import datetime, timedelta


class ReportController:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.sale_repo = SaleRepository()
        self.expense_repo = ExpenseRepository()

    def get_dashboard_stats(self):
        try:
            result = api.get("/reports/dashboard")
            return result or {
                'products_count': 0, 'total_cost': 0, 'total_value': 0,
                'today_sales': 0, 'today_profit': 0, 'total_profit': 0,
                'total_expense': 0, 'net_profit': 0,
                'cash_sales': 0, 'card_sales': 0, 'debt_sales': 0, 'bonus_total': 0,
            }
        except Exception as e:
            print(f"Error in get_dashboard_stats: {e}")
            return {
                'products_count': 0, 'total_cost': 0, 'total_value': 0,
                'today_sales': 0, 'today_profit': 0, 'total_profit': 0,
                'total_expense': 0, 'net_profit': 0,
                'cash_sales': 0, 'card_sales': 0, 'debt_sales': 0, 'bonus_total': 0,
            }

    def get_daily_sales(self, days=7):
        try:
            result = api.get(f"/reports/daily-sales?days={days}")
            return result or {'dates': [], 'amounts': []}
        except Exception as e:
            print(f"Error in get_daily_sales: {e}")
            return {'dates': [], 'amounts': []}

    def get_monthly_sales(self, months=12):
        try:
            end = datetime.now().date()
            start = end.replace(day=1)
            months_list, amounts = [], []
            for i in range(months):
                d = start + timedelta(days=30 * i)
                month_start = d.replace(day=1)
                if i == months - 1:
                    month_end = end
                else:
                    next_month = month_start + timedelta(days=32)
                    month_end = next_month.replace(day=1) - timedelta(days=1)
                amounts.append(self.sale_repo.get_total_sales(month_start, month_end))
                months_list.append(d.strftime("%b"))
            return {'months': months_list, 'amounts': amounts}
        except Exception as e:
            print(f"Error in get_monthly_sales: {e}")
            return {'months': [], 'amounts': []}

    def get_daily_profit(self, days=7):
        try:
            end = datetime.now().date()
            start = end - timedelta(days=days - 1)
            data = []
            for i in range(days):
                d = start + timedelta(days=i)
                data.append({
                    'date': d.strftime("%d.%m"),
                    'profit': self.sale_repo.get_total_profit(d, d)
                })
            return data
        except Exception as e:
            print(f"Error in get_daily_profit: {e}")
            return []

    def get_daily_cost(self, days=7):
        try:
            end = datetime.now().date()
            start = end - timedelta(days=days - 1)
            data = []
            for i in range(days):
                d = start + timedelta(days=i)
                data.append({'date': d.strftime("%d.%m"), 'amount': 0})
            return data
        except Exception as e:
            print(f"Error in get_daily_cost: {e}")
            return []

    def get_top_products(self, limit=10):
        try:
            result = api.get(f"/reports/top-products?limit={limit}")
            return result or []
        except Exception as e:
            print(f"Error in get_top_products: {e}")
            return []

    def get_total_profit(self, start_date=None, end_date=None):
        try:
            return self.sale_repo.get_total_profit(start_date, end_date)
        except Exception as e:
            print(f"Error in get_total_profit: {e}")
            return 0

    def get_all_sales(self):
        try:
            return self.sale_repo.get_sales_with_items()
        except Exception as e:
            print(f"Error in get_all_sales: {e}")
            return []

    def get_sale_items(self, sale_id):
        try:
            result = api.get(f"/reports/sale-items/{sale_id}")
            return result or []
        except Exception as e:
            print(f"Error in get_sale_items: {e}")
            return []

    def get_payment_stats(self, start_date, end_date):
        try:
            result = api.get(
                f"/reports/payment-stats?start_date={start_date}&end_date={end_date}"
            )
            return result or {
                "naxt_total": 0, "plastik_total": 0, "mixed_total": 0,
                "mixed_cash": 0, "mixed_card": 0, "naxt_profit": 0,
                "plastik_profit": 0, "debt_profit": 0, "total_profit": 0,
                "payment_summary": [],
            }
        except Exception as e:
            print(f"Error in get_payment_stats: {e}")
            return {
                "naxt_total": 0, "plastik_total": 0, "mixed_total": 0,
                "mixed_cash": 0, "mixed_card": 0, "naxt_profit": 0,
                "plastik_profit": 0, "debt_profit": 0, "total_profit": 0,
                "payment_summary": [],
            }

    def get_sales_for_export(self, start_date, end_date):
        try:
            result = api.get(
                f"/reports/sales-for-export?start_date={start_date}&end_date={end_date}"
            )
            return result or []
        except Exception as e:
            print(f"Error in get_sales_for_export: {e}")
            return []
