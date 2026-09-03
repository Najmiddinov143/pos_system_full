# recreate_db.py
import sqlite3
import os
import bcrypt

def recreate_database():
    os.makedirs("database", exist_ok=True)
    
    # Eski database ni o'chirish
    if os.path.exists("database/pos.db"):
        os.remove("database/pos.db")
        print("✅ Eski database o'chirildi!")
    
    conn = sqlite3.connect("database/pos.db")
    cursor = conn.cursor()
    
    # ===== USERS =====
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'cashier')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Users table yaratildi!")
    
    # ===== PRODUCTS =====
    cursor.execute('''
        CREATE TABLE products (
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
    print("✅ Products table yaratildi!")
    
    # ===== SALES =====
    cursor.execute('''
        CREATE TABLE sales (
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
            discount_amount REAL DEFAULT 0,
            bonus_amount REAL DEFAULT 0,
            is_debt INTEGER DEFAULT 0,
            debt_paid INTEGER DEFAULT 0,
            customer_name TEXT,
            customer_phone TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("✅ Sales table yaratildi!")
    
    # ===== SALE ITEMS =====
    cursor.execute('''
        CREATE TABLE sale_items (
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
    print("✅ Sale_items table yaratildi!")
    
    # ===== EXPENSES =====
    cursor.execute('''
        CREATE TABLE expenses (
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
    print("✅ Expenses table yaratildi!")
    
    # ===== EMPLOYEES =====
    cursor.execute('''
        CREATE TABLE employees (
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
    print("✅ Employees table yaratildi!")
    
    # ===== BACKUP HISTORY =====
    cursor.execute('''
        CREATE TABLE backup_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            backup_date TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_size INTEGER,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Backup_history table yaratildi!")
    
    # ===== NOTIFICATIONS =====
    cursor.execute('''
        CREATE TABLE notifications (
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
    print("✅ Notifications table yaratildi!")
    
    # ===== SHOP SETTINGS =====
    cursor.execute('''
        CREATE TABLE shop_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_name TEXT NOT NULL DEFAULT 'Moy almashtirish',
            address TEXT,
            phone TEXT,
            logo_path TEXT,
            receipt_footer TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Shop_settings table yaratildi!")
    
    # ===== ATTENDANCE =====
    cursor.execute('''
        CREATE TABLE attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            check_in TEXT,
            check_out TEXT,
            date TEXT NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    ''')
    print("✅ Attendance table yaratildi!")
    
    # ===== SETTINGS =====
    cursor.execute('''
        CREATE TABLE settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Settings table yaratildi!")
    
    # ===== DEBTS =====
    cursor.execute('''
        CREATE TABLE debts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            customer_phone TEXT,
            total_amount REAL NOT NULL,
            paid_amount REAL DEFAULT 0,
            remaining_amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TEXT,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (sale_id) REFERENCES sales(id)
        )
    ''')
    print("✅ Debts table yaratildi!")
    
    # ===== INVENTORY LOGS =====
    cursor.execute('''
        CREATE TABLE inventory_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            quantity REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    print("✅ Inventory_logs table yaratildi!")
    
    # ===== DEFAULT USERS =====
    pwd = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                  ('admin', pwd, 'admin'))
    print("✅ Admin user yaratildi: admin / admin123")
    
    pwd = bcrypt.hashpw("cashier123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                  ('cashier', pwd, 'cashier'))
    print("✅ Cashier user yaratildi: cashier / cashier123")
    
    # ===== DEFAULT SHOP SETTINGS =====
    cursor.execute('''
        INSERT INTO shop_settings (shop_name, address, phone, receipt_footer)
        VALUES (?, ?, ?, ?)
    ''', ('Moy almashtirish', 'Toshkent sh.', '+998 99 123 45 67', 'Rahmat! Xush kelibsiz!'))
    print("✅ Shop settings yaratildi!")
    
    # ===== DEFAULT SETTINGS =====
    cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ('notification_enabled', 'true'))
    cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ('sound_enabled', 'true'))
    print("✅ Default settings yaratildi!")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print("✅ Database muvaffaqiyatli qayta yaratildi!")
    print("👤 Admin: admin / admin123")
    print("👤 Kassir: cashier / cashier123")
    print("="*50)

if __name__ == "__main__":
    recreate_database() 