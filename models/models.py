# # # models/models.py
# # from dataclasses import dataclass
# # from datetime import datetime
# # from typing import Optional, List

# # @dataclass
# # class Expense:
# #     id: Optional[int] = None
# #     name: str = ""
# #     amount: float = 0.0
# #     category: str = ""
# #     description: str = ""
# #     created_at: datetime = None
# #     user_id: Optional[int] = None

# # @dataclass
# # class User:
# #     id: Optional[int] = None
# #     username: str = ""
# #     password_hash: str = ""
# #     role: str = "cashier"
# #     created_at: datetime = None

# # @dataclass
# # class Product:
# #     id: Optional[int] = None
# #     name: str = ""
# #     category: str = ""
# #     cost_price: float = 0.0
# #     sell_price: float = 0.0
# #     quantity: float = 0.0
# #     unit: str = "dona"
# #     min_quantity: float = 5
# #     note: str = ""
# #     created_at: datetime = None

# # @dataclass
# # class Sale:
# #     id: Optional[int] = None
# #     total_amount: float = 0.0
# #     total_profit: float = 0.0
# #     discount: float = 0.0
# #     created_at: datetime = None
# #     user_id: Optional[int] = None
# #     car_number: str = ""
# #     car_model: str = ""
# #     current_km: float = 0.0
# #     next_km: float = 0.0
# #     oil_change_date: str = ""
# #     next_oil_change_date: str = ""
# #     notification_date: str = ""  # Yangi
# #     is_notified: int = 0         # Yangi
# #     items: List['SaleItem'] = None

# # @dataclass
# # class SaleItem:
# #     id: Optional[int] = None
# #     sale_id: Optional[int] = None
# #     product_id: int = 0
# #     quantity: float = 0.0
# #     sell_price: float = 0.0
# #     cost_price: float = 0.0
# #     subtotal: float = 0.0
# #     product_name: Optional[str] = None

# # @dataclass
# # class InventoryLog:
# #     id: Optional[int] = None
# #     product_id: int = 0
# #     action: str = ""
# #     quantity: float = 0.0
# #     created_at: datetime = None
# #     user_id: Optional[int] = None
# #     # models/models.py - oxiriga qo'shing
# # @dataclass
# # class Expense:
# #     id: Optional[int] = None
# #     name: str = ""
# #     amount: float = 0.0
# #     category: str = ""
# #     description: str = ""
# #     created_at: datetime = None
# #     user_id: Optional[int] = None

# # models/models.py

# from dataclasses import dataclass
# from datetime import datetime
# from typing import Optional, List

# # models/models.py - qo'shing

# @dataclass
# class Notification:
#     id: Optional[int] = None
#     title: str = ""
#     message: str = ""
#     type: str = ""
#     is_read: int = 0
#     user_id: Optional[int] = None
#     created_at: datetime = None

# @dataclass
# class Employee:
#     id: Optional[int] = None
#     full_name: str = ""
#     phone: str = ""
#     position: str = ""
#     salary: float = 0.0
#     hire_date: str = ""
#     is_active: int = 1
#     created_at: datetime = None

# @dataclass
# class Backup:
#     id: Optional[int] = None
#     backup_date: str = ""
#     file_name: str = ""
#     file_size: int = 0
#     created_by: Optional[int] = None
#     created_at: datetime = None

# @dataclass
# class Notification:
#     id: Optional[int] = None
#     title: str = ""
#     message: str = ""
#     type: str = ""
#     is_read: int = 0
#     user_id: Optional[int] = None
#     created_at: datetime = None

# @dataclass
# class ShopSettings:
#     id: Optional[int] = None
#     shop_name: str = ""
#     address: str = ""
#     phone: str = ""
#     logo_path: str = ""
#     receipt_footer: str = ""
#     updated_at: datetime = None

# @dataclass
# class Attendance:
#     id: Optional[int] = None
#     employee_id: int = 0
#     check_in: str = ""
#     check_out: str = ""
#     date: str = ""
    
# @dataclass
# class User:
#     id: Optional[int] = None
#     username: str = ""
#     password_hash: str = ""
#     role: str = "cashier"
#     created_at: datetime = None

# # models/models.py
# @dataclass
# class Product:
#     id: Optional[int] = None
#     name: str = ""
#     category: str = ""
#     cost_price: float = 0.0
#     sell_price: float = 0.0
#     quantity: float = 0.0
#     unit: str = "dona"
#     min_quantity: float = 5
#     note: str = ""
#     image_path: str = ""  # YANGI
#     barcode: str = ""     # YANGI
#     supplier: str = ""    # YANGI
#     created_at: datetime = None

# # models/models.py - Sale klassiga
# # models/models.py - Sale klassiga qo'shing
# @dataclass
# class Sale:
#     # ... oldingi maydonlar ...
#     payment_type: str = "Naxt"  # Naxt, Plastik, Nasiya
#     discount_amount: float = 0.0
#     bonus_amount: float = 0.0
#     is_debt: int = 0
#     debt_paid: int = 0
#     customer_name: str = ""
#     customer_phone: str = ""

# @dataclass
# class Debt:
#     id: Optional[int] = None
#     sale_id: int = 0
#     customer_name: str = ""
#     customer_phone: str = ""
#     total_amount: float = 0.0
#     paid_amount: float = 0.0
#     remaining_amount: float = 0.0
#     created_at: datetime = None
#     due_date: str = ""
#     status: str = "active"
    
# @dataclass
# class SaleItem:
#     id: Optional[int] = None
#     sale_id: Optional[int] = None
#     product_id: int = 0
#     quantity: float = 0.0
#     sell_price: float = 0.0
#     cost_price: float = 0.0
#     subtotal: float = 0.0
#     product_name: Optional[str] = None

# @dataclass
# class Expense:
#     id: Optional[int] = None
#     name: str = ""
#     amount: float = 0.0
#     category: str = ""
#     description: str = ""
#     created_at: datetime = None
#     user_id: Optional[int] = None

# @dataclass
# class InventoryLog:
#     id: Optional[int] = None
#     product_id: int = 0
#     action: str = ""
#     quantity: float = 0.0
#     created_at: datetime = None
#     user_id: Optional[int] = None


# models/models.py
# from dataclasses import dataclass
# from datetime import datetime
# from typing import Optional, List

# @dataclass
# class User:
#     id: Optional[int] = None
#     username: str = ""
#     password_hash: str = ""
#     role: str = "cashier"
#     created_at: datetime = None

# @dataclass
# class Product:
#     id: Optional[int] = None
#     name: str = ""
#     category: str = ""
#     cost_price: float = 0.0
#     sell_price: float = 0.0
#     quantity: float = 0.0
#     unit: str = "dona"
#     min_quantity: float = 5
#     note: str = ""
#     image_path: str = ""
#     barcode: str = ""
#     supplier: str = ""
#     created_at: datetime = None

# @dataclass
# class Sale:
#     id: Optional[int] = None
#     total_amount: float = 0.0
#     total_profit: float = 0.0
#     discount: float = 0.0
#     created_at: datetime = None
#     user_id: Optional[int] = None
#     car_number: str = ""
#     car_model: str = ""
#     phone_number: str = ""
#     current_km: float = 0.0
#     next_km: float = 0.0
#     oil_change_date: str = ""
#     next_oil_change_date: str = ""
#     notification_date: str = ""
#     is_notified: int = 0
#     payment_type: str = "Naxt"
#     bonus_amount: float = 0.0
#     discount_amount: float = 0.0
#     is_debt: int = 0
#     debt_paid: int = 0
#     customer_name: str = ""
#     customer_phone: str = ""
#     items: List['SaleItem'] = None

# @dataclass
# class SaleItem:
#     id: Optional[int] = None
#     sale_id: Optional[int] = None
#     product_id: int = 0
#     quantity: float = 0.0
#     sell_price: float = 0.0
#     cost_price: float = 0.0
#     subtotal: float = 0.0
#     product_name: Optional[str] = None

# @dataclass
# class Expense:
#     id: Optional[int] = None
#     name: str = ""
#     amount: float = 0.0
#     category: str = ""
#     description: str = ""
#     created_at: datetime = None
#     user_id: Optional[int] = None

# @dataclass
# class Employee:
#     id: Optional[int] = None
#     full_name: str = ""
#     phone: str = ""
#     position: str = ""
#     salary: float = 0.0
#     hire_date: str = ""
#     is_active: int = 1
#     created_at: datetime = None

# @dataclass
# class Notification:
#     id: Optional[int] = None
#     title: str = ""
#     message: str = ""
#     type: str = ""
#     is_read: int = 0
#     user_id: Optional[int] = None
#     created_at: datetime = None

# @dataclass
# class InventoryLog:
#     id: Optional[int] = None
#     product_id: int = 0
#     action: str = ""
#     quantity: float = 0.0
#     created_at: datetime = None
#     user_id: Optional[int] = None





# models/models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    role: str = "cashier"
    created_at: datetime = None

@dataclass
class Product:
    id: Optional[int] = None
    name: str = ""
    category: str = ""
    cost_price: float = 0.0
    sell_price: float = 0.0
    quantity: float = 0.0
    unit: str = "dona"
    min_quantity: float = 5
    note: str = ""
    image_path: str = ""
    barcode: str = ""
    supplier: str = ""
    cost_price_usd: float = 0.0   # Tannarx dollarda (mahsulot xorijdan $ da kelsa)
    exchange_rate: float = 0.0    # Shu mahsulot uchun ishlatilgan kurs (1$ = necha so'm)
    created_at: datetime = None

@dataclass
class Sale:
    id: Optional[int] = None
    total_amount: float = 0.0
    total_profit: float = 0.0
    discount: float = 0.0
    created_at: datetime = None
    user_id: Optional[int] = None
    car_number: str = ""
    car_model: str = ""
    phone_number: str = ""  # Tepadagi koddan
    current_km: float = 0.0
    next_km: float = 0.0
    oil_change_date: str = ""
    next_oil_change_date: str = ""
    notification_date: str = ""
    is_notified: int = 0
    payment_type: str = "Naxt"
    bonus_amount: float = 0.0
    discount_amount: float = 0.0
    cash_amount: float = 0.0   # "Naxt + Plastik" aralash to'lovda - naqd qismi
    card_amount: float = 0.0   # "Naxt + Plastik" aralash to'lovda - plastik qismi
    extra_charge: float = 0.0  # Kassir "Yakuniy" summani qo'lda o'zgartirsa - farq shu yerda
    is_debt: int = 0
    debt_paid: int = 0
    customer_name: str = ""
    customer_phone: str = ""  # Izohlardagi koddan
    items: List['SaleItem'] = None

@dataclass
class SaleItem:
    id: Optional[int] = None
    sale_id: Optional[int] = None
    product_id: int = 0
    quantity: float = 0.0
    sell_price: float = 0.0
    cost_price: float = 0.0
    subtotal: float = 0.0
    product_name: Optional[str] = None

@dataclass
class Expense:
    id: Optional[int] = None
    name: str = ""
    amount: float = 0.0
    category: str = ""
    description: str = ""
    payment_type: str = "Naxt"  # Naxt yoki Plastik - qaysi kassadan yechilganini bildiradi
    created_at: datetime = None
    user_id: Optional[int] = None
    id: Optional[int] = None
    full_name: str = ""
    phone: str = ""
    position: str = ""
    salary: float = 0.0
    hire_date: str = ""
    is_active: int = 1
    created_at: datetime = None

@dataclass
class Employee:
    id: Optional[int] = None
    full_name: str = ""
    phone: str = ""
    position: str = ""
    salary: float = 0.0
    hire_date: str = ""
    is_active: int = 1
    created_at: datetime = None

@dataclass
class Notification:
    id: Optional[int] = None
    title: str = ""
    message: str = ""
    type: str = ""
    is_read: int = 0
    user_id: Optional[int] = None
    created_at: datetime = None

@dataclass
class InventoryLog:
    id: Optional[int] = None
    product_id: int = 0
    action: str = ""
    quantity: float = 0.0
    created_at: datetime = None
    user_id: Optional[int] = None

# ---- QUYIDAGILAR FAQAT IKKINCHI VARIANTDA BOR EDI, KODGA QO'SHILDI ----

@dataclass
class Backup:
    id: Optional[int] = None
    backup_date: str = ""
    file_name: str = ""
    file_size: int = 0
    created_by: Optional[int] = None
    created_at: datetime = None

@dataclass
class ShopSettings:
    id: Optional[int] = None
    shop_name: str = ""
    address: str = ""
    phone: str = ""
    logo_path: str = ""
    receipt_footer: str = ""
    updated_at: datetime = None

@dataclass
class Attendance:
    id: Optional[int] = None
    employee_id: int = 0
    check_in: str = ""
    check_out: str = ""
    date: str = ""

@dataclass
class Debt:
    id: Optional[int] = None
    sale_id: int = 0
    customer_name: str = ""
    customer_phone: str = ""
    total_amount: float = 0.0
    paid_amount: float = 0.0
    remaining_amount: float = 0.0
    created_at: datetime = None
    due_date: str = ""
    status: str = "active"