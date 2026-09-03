# migrate_db.py - TO'LIQ TUZATILGAN

import sqlite3
import os
import bcrypt
from datetime import datetime

def create_database():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect("database/pos.db")
    cursor = conn.cursor()
    
    # ===== 1. Users table =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'cashier')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ===== 2. Products table =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            cost_price REAL NOT NULL,
            sell_price REAL NOT NULL,
            quantity REAL NOT NULL DEFAULT 0,
            unit TEXT DEFAULT 'dona',
            min_quantity REAL DEFAULT 5,
            note TEXT,
            image_path TEXT,
            barcode TEXT,
            supplier TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ===== 3. Sales table =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_amount REAL NOT NULL,
            total_profit REAL NOT NULL,
            discount REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            car_number TEXT,
            car_model TEXT,
            phone_number TEXT,
            current_km REAL DEFAULT 0,
            next_km REAL DEFAULT 0,
            oil_change_date TEXT,
            next_oil_change_date TEXT,
            notification_date TEXT,
            is_notified INTEGER DEFAULT 0,
            payment_type TEXT DEFAULT 'Naxt',
            bonus_amount REAL DEFAULT 0,
            discount_amount REAL DEFAULT 0,
            is_debt INTEGER DEFAULT 0,
            debt_paid INTEGER DEFAULT 0,
            customer_name TEXT,
            customer_phone TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # ===== 4. Sale items table =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            sell_price REAL NOT NULL,
            cost_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # ===== 5. Expenses table =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # ===== 6. Inventory logs table =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            quantity REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # ===== 7. Employees table =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT,
            position TEXT NOT NULL,
            salary REAL DEFAULT 0,
            hire_date TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ===== 8. Backup history table =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS backup_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            backup_date TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_size INTEGER,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ===== 9. Notifications table =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # ===== 10. Shop settings table =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shop_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_name TEXT NOT NULL DEFAULT 'Moy almashtirish',
            address TEXT,
            phone TEXT,
            logo_path TEXT,
            receipt_footer TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ===== 11. Attendance table =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            check_in TEXT,
            check_out TEXT,
            date TEXT NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    ''')
    
    # ===== 12. Settings table =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ===== 13. Stock purchases (Naxt/Nasiya xaridlari) =====
    # 🔥 remaining_debt va paid_date ustunlari qo'shilgan
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            product_name TEXT,
            quantity REAL NOT NULL,
            unit_cost REAL NOT NULL,
            total_cost REAL NOT NULL,
            payment_type TEXT DEFAULT 'Naxt' CHECK(payment_type IN ('Naxt', 'Nasiya')),
            purchase_date TEXT NOT NULL,
            due_date TEXT,
            is_paid INTEGER DEFAULT 0,
            paid_date TEXT,
            remaining_debt REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # ===== ADMIN VA CASHIER =====
    admin_pwd = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute('INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                   ('admin', admin_pwd, 'admin'))
    
    cashier_pwd = bcrypt.hashpw('cashier123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute('INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                   ('cashier', cashier_pwd, 'cashier'))
    
    # ===== SHOP SETTINGS =====
    cursor.execute('SELECT * FROM shop_settings')
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO shop_settings (shop_name, address, phone, receipt_footer)
            VALUES (?, ?, ?, ?)
        ''', ('Moy almashtirish', 'Toshkent sh., ...', '+998 99 123 45 67', 'Rahmat! Xush kelibsiz!'))
    
    # ===== DEFAULT EMPLOYEE =====
    cursor.execute('SELECT * FROM employees')
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO employees (full_name, phone, position, salary, hire_date)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Admin', '+998 99 111 22 33', 'Admin', 0, '2024-01-01'))
    
    conn.commit()
    conn.close()
    
    print('=' * 50)
    print('✅ Ma\'lumotlar bazasi muvaffaqiyatli yaratildi!')
    print('=' * 50)
    print('📊 Jadvallar:')
    print('  - users')
    print('  - products')
    print('  - sales')
    print('  - sale_items')
    print('  - expenses')
    print('  - inventory_logs')
    print('  - employees')
    print('  - backup_history')
    print('  - notifications')
    print('  - shop_settings')
    print('  - attendance')
    print('  - settings')
    print('  - stock_purchases (Naxt/Nasiya)')
    print('')
    print('👤 Admin: admin / admin123')
    print('👤 Kassir: cashier / cashier123')
    print('=' * 50)

def migrate_database():
    """Mavjud ma'lumotlar bazasini yangilash"""
    db_path = "database/pos.db"
    
    if not os.path.exists(db_path):
        print("❌ Ma'lumotlar bazasi topilmadi! Yangi yaratilmoqda...")
        create_database()
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Ma'lumotlar bazasi yangilanmoqda...")
    
    # ===== 1. stock_purchases jadvaliga paid_date ustunini qo'shish =====
    try:
        cursor.execute("ALTER TABLE stock_purchases ADD COLUMN paid_date TEXT")
        print("✅ paid_date ustuni qo'shildi!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✅ paid_date ustuni allaqachon mavjud")
        else:
            print(f"⚠️ paid_date: {e}")
    
    # ===== 2. stock_purchases jadvaliga remaining_debt ustunini qo'shish =====
    try:
        cursor.execute("ALTER TABLE stock_purchases ADD COLUMN remaining_debt REAL DEFAULT 0")
        print("✅ remaining_debt ustuni qo'shildi!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✅ remaining_debt ustuni allaqachon mavjud")
        else:
            print(f"⚠️ remaining_debt: {e}")
    
    # ===== 3. products jadvaliga image_path ustunini qo'shish =====
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN image_path TEXT")
        print("✅ image_path ustuni qo'shildi!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✅ image_path ustuni allaqachon mavjud")
        else:
            print(f"⚠️ image_path: {e}")
    
    # ===== 4. products jadvaliga barcode ustunini qo'shish =====
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN barcode TEXT")
        print("✅ barcode ustuni qo'shildi!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✅ barcode ustuni allaqachon mavjud")
        else:
            print(f"⚠️ barcode: {e}")
    
    # ===== 5. products jadvaliga supplier ustunini qo'shish =====
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN supplier TEXT")
        print("✅ supplier ustuni qo'shildi!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✅ supplier ustuni allaqachon mavjud")
        else:
            print(f"⚠️ supplier: {e}")
    
    # ===== 6. sales jadvaliga yangi ustunlarni qo'shish =====
    sales_columns = [
        ('phone_number', 'TEXT'),
        ('payment_type', "TEXT DEFAULT 'Naxt'"),
        ('bonus_amount', 'REAL DEFAULT 0'),
        ('discount_amount', 'REAL DEFAULT 0'),
        ('is_debt', 'INTEGER DEFAULT 0'),
        ('debt_paid', 'INTEGER DEFAULT 0'),
        ('customer_name', 'TEXT'),
        ('customer_phone', 'TEXT')
    ]
    
    for col_name, col_type in sales_columns:
        try:
            cursor.execute(f"ALTER TABLE sales ADD COLUMN {col_name} {col_type}")
            print(f"✅ sales.{col_name} ustuni qo'shildi!")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"✅ sales.{col_name} ustuni allaqachon mavjud")
            else:
                print(f"⚠️ sales.{col_name}: {e}")
    
    conn.commit()
    conn.close()
    
    print('=' * 50)
    print('✅ Ma\'lumotlar bazasi muvaffaqiyatli yangilandi!')
    print('=' * 50)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'migrate':
        migrate_database()
    else:
        create_database()