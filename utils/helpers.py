# utils/helpers.py

from datetime import datetime, timedelta
import bcrypt

def format_price(amount):
    return f"{amount:,.2f} so'm"

def format_date(dt):
    return dt.strftime("%d.%m.%Y %H:%M")

def get_today_date():
    return datetime.now().date()

def get_week_dates():
    today = get_today_date()
    start = today - timedelta(days=today.weekday())
    return start, today

def get_month_dates():
    today = get_today_date()
    start = today.replace(day=1)
    return start, today

def validate_quantity(qty):
    try:
        qty = float(qty)
        if qty < 0:
            return False
        return True
    except ValueError:
        return False

def generate_receipt_number():
    now = datetime.now()
    return f"RCP-{now.strftime('%Y%m%d%H%M%S')}"

def hash_password(password):
    """Parolni hash qilish"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    """Parolni tekshirish"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def format_currency(amount):
    """Pulni formatlash"""
    return f"{amount:,.0f}"

def parse_date(date_str):
    """Sanani parse qilish"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return None

def days_between(date1, date2):
    """Ikki sana orasidagi kunlar"""
    if date1 and date2:
        return (date2 - date1).days
    return 0

def get_current_time():
    """Hozirgi vaqt"""
    return datetime.now().strftime("%H:%M:%S")

def get_current_date():
    """Hozirgi sana"""
    return datetime.now().strftime("%Y-%m-%d")