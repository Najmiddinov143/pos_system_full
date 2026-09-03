# controllers/sale_controller.py - TO'LIQ

from models.repositories import SaleRepository, ProductRepository
from models.models import Sale, SaleItem
from datetime import datetime

class SaleController:
    def __init__(self):
        self.sale_repo = SaleRepository()
        self.product_repo = ProductRepository()
    
    def create_sale(self, sale, items):
        return self.sale_repo.create_sale(sale, items)
    
    def create(self, sale, items):
        return self.create_sale(sale, items)
    
    def get_sales_by_date_range(self, start_date, end_date):
        try:
            sales = self.sale_repo.get_sales_with_items(start_date, end_date)
            result = []
            for sale in sales:
                created_at_str = ""
                if sale.created_at:
                    if hasattr(sale.created_at, 'strftime'):
                        created_at_str = sale.created_at.strftime("%Y-%m-%d %H:%M")
                    else:
                        created_at_str = str(sale.created_at)
                
                result.append({
                    'id': sale.id,
                    'total_amount': sale.total_amount,
                    'total_profit': sale.total_profit,
                    'discount': sale.discount,
                    'created_at': created_at_str,
                    'user_id': sale.user_id,
                    'car_number': sale.car_number,
                    'car_model': sale.car_model,
                    'phone_number': sale.phone_number,
                    'current_km': sale.current_km,
                    'next_km': sale.next_km,
                    'oil_change_date': sale.oil_change_date,
                    'next_oil_change_date': sale.next_oil_change_date,
                    'payment_type': sale.payment_type,
                    'bonus_amount': sale.bonus_amount,
                    'discount_amount': sale.discount_amount,
                    'is_debt': sale.is_debt,
                    'debt_paid': sale.debt_paid,
                    'customer_name': sale.customer_name,
                    'customer_phone': sale.customer_phone
                })
            return result
        except Exception as e:
            print(f"Error in get_sales_by_date_range: {e}")
            return []
    
    def get_sale_by_id(self, sale_id):
        try:
            sales = self.sale_repo.get_sales_with_items()
            for sale in sales:
                if sale.id == sale_id:
                    created_at_str = ""
                    if sale.created_at:
                        if hasattr(sale.created_at, 'strftime'):
                            created_at_str = sale.created_at.strftime("%Y-%m-%d %H:%M")
                        else:
                            created_at_str = str(sale.created_at)
                    
                    return {
                        'id': sale.id,
                        'total_amount': sale.total_amount,
                        'total_profit': sale.total_profit,
                        'discount': sale.discount,
                        'created_at': created_at_str,
                        'user_id': sale.user_id,
                        'car_number': sale.car_number,
                        'car_model': sale.car_model,
                        'phone_number': sale.phone_number,
                        'current_km': sale.current_km,
                        'next_km': sale.next_km,
                        'oil_change_date': sale.oil_change_date,
                        'next_oil_change_date': sale.next_oil_change_date,
                        'payment_type': sale.payment_type,
                        'bonus_amount': sale.bonus_amount,
                        'discount_amount': sale.discount_amount,
                        'is_debt': sale.is_debt,
                        'debt_paid': sale.debt_paid,
                        'customer_name': sale.customer_name,
                        'customer_phone': sale.customer_phone
                    }
            return None
        except Exception as e:
            print(f"Error in get_sale_by_id: {e}")
            return None

    def get_sale_items(self, sale_id):
        try:
            sales = self.sale_repo.get_sales_with_items()
            for sale in sales:
                if sale.id == sale_id:
                    items = []
                    for item in sale.items:
                        product = self.product_repo.get_product_by_id(item.product_id)
                        items.append({
                            'product_name': item.product_name or '',
                            'quantity': item.quantity,
                            'sell_price': item.sell_price,
                            'cost_price': item.cost_price,
                            'subtotal': item.subtotal,
                            'unit': product['unit'] if product and product.get('unit') else 'dona'
                        })
                    return items
            return []
        except Exception as e:
            print(f"Error in get_sale_items: {e}")
            return []
    
    def get_all_sales(self):
        try:
            sales = self.sale_repo.get_sales_with_items()
            result = []
            for sale in sales:
                created_at_str = ""
                if sale.created_at:
                    if hasattr(sale.created_at, 'strftime'):
                        created_at_str = sale.created_at.strftime("%Y-%m-%d %H:%M")
                    else:
                        created_at_str = str(sale.created_at)
                
                result.append({
                    'id': sale.id,
                    'total_amount': sale.total_amount,
                    'total_profit': sale.total_profit,
                    'discount': sale.discount,
                    'created_at': created_at_str,
                    'user_id': sale.user_id,
                    'car_number': sale.car_number,
                    'car_model': sale.car_model,
                    'phone_number': sale.phone_number,
                    'current_km': sale.current_km,
                    'next_km': sale.next_km,
                    'oil_change_date': sale.oil_change_date,
                    'next_oil_change_date': sale.next_oil_change_date,
                    'payment_type': sale.payment_type,
                    'bonus_amount': sale.bonus_amount,
                    'discount_amount': sale.discount_amount,
                    'is_debt': sale.is_debt,
                    'debt_paid': sale.debt_paid,
                    'customer_name': sale.customer_name,
                    'customer_phone': sale.customer_phone
                })
            return result
        except Exception as e:
            print(f"Error in get_all_sales: {e}")
            return []

    def get_upcoming_notifications(self, days=3):
        try:
            return self.sale_repo.get_upcoming_notifications(days)
        except Exception as e:
            print(f"Error in get_upcoming_notifications: {e}")
            return []

    def mark_as_notified(self, sale_id):
        try:
            return self.sale_repo.mark_as_notified(sale_id)
        except Exception as e:
            print(f"Error in mark_as_notified: {e}") 
            return False

    def update_payment_type(self, sale_id, new_payment_type, customer_name="", customer_phone=""):
        try:
            return self.sale_repo.update_payment_type(sale_id, new_payment_type, customer_name, customer_phone)
        except Exception as e:
            print(f"❌ Error updating payment type: {e}")
            return False

    def update_sale(self, sale_id, update_data):
        try:
            return self.sale_repo.update_sale(sale_id, update_data)
        except Exception as e:
            print(f"❌ Error updating sale: {e}")
            return False

    # ===== YANGI: Sana bo'yicha sotuvlarni olish =====
    def get_sales_by_date(self, date_str):
        try:
            sales = self.sale_repo.get_sales_by_date(date_str)
            result = []
            for sale in sales:
                result.append({
                    'id': sale['id'],
                    'total_amount': sale['total_amount'],
                    'total_profit': sale['total_profit']
                })
            return result
        except Exception as e:
            print(f"Error in get_sales_by_date: {e}")
            return []
    
# ===== YANGI: kunlik naqd/plastik balansini olish =====
    def get_cash_card_balance(self, date_str):
        try:
            return self.sale_repo.get_cash_card_balance(date_str)
        except Exception as e:
            print(f"❌ Error in get_cash_card_balance: {e}")
            return {'total_cash': 0.0, 'total_card': 0.0, 'available_cash': 0.0, 'available_card': 0.0}

    # ===== YANGI: qarz to'langanda savdo yozuvidan bir marta ayirish =====
    def reduce_sale_by_payment(self, sale_id, total_delta, cash_delta, card_delta):
        try:
            return self.sale_repo.reduce_sale_by_payment(sale_id, total_delta, cash_delta, card_delta)
        except Exception as e:
            print(f"❌ Error in reduce_sale_by_payment: {e}")
            return False