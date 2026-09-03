# database/database.py - TO'LIQ YANGILANGAN (Firmalar qo'shildi)

import sqlite3
import bcrypt
from datetime import datetime
from pathlib import Path
import json
import os

class Database:
    def __init__(self, db_path="database/pos.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.create_tables()
        self.migrate_schema()
        self.seed_data()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # ===== 1. USERS =====
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'cashier')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ===== 2. PRODUCTS =====
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
                is_active INTEGER DEFAULT 1,
                dollar_cost REAL DEFAULT 0,
                dollar_price REAL DEFAULT 0,
                exchange_rate REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ===== 3. SALES =====
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
                cash_amount REAL DEFAULT 0,
                card_amount REAL DEFAULT 0,
                extra_charge REAL DEFAULT 0,
                is_debt INTEGER DEFAULT 0,
                debt_paid INTEGER DEFAULT 0,
                customer_name TEXT,
                customer_phone TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # ===== 4. SALE ITEMS =====
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
        
        # ===== 5. EXPENSES =====
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
        
        # ===== 6. INVENTORY LOGS =====
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
        
        # ===== 7. EMPLOYEES =====
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
        
        # ===== 8. BACKUP HISTORY =====
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
        
        # ===== 9. NOTIFICATIONS =====
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT DEFAULT 'Eslatma',
                is_read INTEGER DEFAULT 0,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # ===== 10. SHOP SETTINGS =====
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
        
        # ===== 11. ATTENDANCE =====
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
        
        # ===== 12. SETTINGS =====
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ===== 13. STOCK PURCHASES (TUZATILGAN - DUPLIKATLAR O'CHIRILDI) =====
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                product_name TEXT,
                quantity REAL NOT NULL,
                unit_cost REAL NOT NULL,
                total_cost REAL NOT NULL,
                dollar_cost REAL DEFAULT 0,
                dollar_price REAL DEFAULT 0,
                exchange_rate REAL DEFAULT 0,
                payment_type TEXT DEFAULT 'Naxt' CHECK(payment_type IN ('Naxt', 'Nasiya')),
                purchase_date TEXT NOT NULL,
                due_date TEXT,
                is_paid INTEGER DEFAULT 0,
                paid_date TEXT,
                remaining_debt REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                firm_id INTEGER,
                FOREIGN KEY (product_id) REFERENCES products(id),
                FOREIGN KEY (firm_id) REFERENCES firms(id)
            )
        ''')
        
        # ===== 14. CASH INCOMES =====
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cash_incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # ===== 15. FIRMS (YANGI) =====
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS firms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                total_debt REAL DEFAULT 0,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ===== 16. FIRM DEBTS (YANGI) =====
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS firm_debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firm_id INTEGER NOT NULL,
                firm_name TEXT,
                amount REAL NOT NULL,
                description TEXT,
                debt_type TEXT DEFAULT 'qarz' CHECK(debt_type IN ('qarz', 'to_lov')),
                is_paid INTEGER DEFAULT 0,
                paid_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (firm_id) REFERENCES firms(id)
            )
        ''')
        
        # ===== 17. CATEGORIES (YANGI) =====
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                parent_id INTEGER,
                icon TEXT,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES categories(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Barcha jadvallar yaratildi (firms, firm_debts va categories bilan)!")
    
    def migrate_schema(self):
        """Eski bazalarga yangi ustunlarni qo'shish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        migrations = {
            'sales': [
                ('cash_amount', 'REAL DEFAULT 0'),
                ('card_amount', 'REAL DEFAULT 0'),
                ('extra_charge', 'REAL DEFAULT 0'),
                ('customer_name', 'TEXT'),
                ('customer_phone', 'TEXT'),
            ],
            'products': [
                ('is_active', 'INTEGER DEFAULT 1'),
                ('dollar_cost', 'REAL DEFAULT 0'),
                ('dollar_price', 'REAL DEFAULT 0'),
                ('exchange_rate', 'REAL DEFAULT 0'),
                ('barcode', 'TEXT'),
                ('supplier', 'TEXT'),
                ('category_id', 'INTEGER REFERENCES categories(id)'),  # QO'SHILDI
            ],
            'stock_purchases': [
                ('dollar_cost', 'REAL DEFAULT 0'),
                ('dollar_price', 'REAL DEFAULT 0'),
                ('exchange_rate', 'REAL DEFAULT 0'),
                ('remaining_debt', 'REAL DEFAULT 0'),
                ('paid_date', 'TEXT'),
                ('firm_id', 'INTEGER'),
            ],
            'notifications': [
                ('type', "TEXT DEFAULT 'Eslatma'"),
                ('is_read', 'INTEGER DEFAULT 0'),
                ('user_id', 'INTEGER'),
            ],
            'employees': [
                ('is_active', 'INTEGER DEFAULT 1'),
            ],
            'firms': [
                ('total_debt', 'REAL DEFAULT 0'),
                ('note', 'TEXT'),
            ],
            'firm_debts': [
                ('firm_name', 'TEXT'),
                ('is_paid', 'INTEGER DEFAULT 0'),
                ('paid_date', 'TEXT'),
            ],
        }
        
        for table, columns in migrations.items():
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                existing_columns = {row[1] for row in cursor.fetchall()}
            except Exception as e:
                print(f"⚠️ '{table}' jadvali tekshirilmadi: {e}")
                continue
            
            for col_name, col_def in columns:
                if col_name not in existing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
                        print(f"✅ Migratsiya: '{table}' jadvaliga '{col_name}' ustuni qo'shildi")
                    except Exception as e:
                        print(f"❌ Migratsiya xatosi ({table}.{col_name}): {e}")
        
        # firm_debts jadvali borligini tekshirish
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='firm_debts'")
        if not cursor.fetchone():
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS firm_debts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    firm_id INTEGER NOT NULL,
                    firm_name TEXT,
                    amount REAL NOT NULL,
                    description TEXT,
                    debt_type TEXT DEFAULT 'qarz' CHECK(debt_type IN ('qarz', 'to_lov')),
                    is_paid INTEGER DEFAULT 0,
                    paid_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (firm_id) REFERENCES firms(id)
                )
            ''')
            print("✅ firm_debts jadvali qo'shildi!")
        
        # categories jadvali borligini tekshirish
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'")
        if not cursor.fetchone():
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    parent_id INTEGER,
                    icon TEXT,
                    color TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES categories(id)
                )
            ''')
            print("✅ categories jadvali qo'shildi!")
        
        conn.commit()
        conn.close()
        self.cleanup_float_precision()
    
    def cleanup_float_precision(self):
        """Oldingi versiyalarda yuzaga kelgan floating-point xatolarini tuzatish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, quantity FROM products")
            rows = cursor.fetchall()
            for row in rows:
                fixed = round(row['quantity'], 3)
                if abs(fixed) < 0.001:
                    fixed = 0
                if fixed != row['quantity']:
                    cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (fixed, row['id']))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Floating-point tozalashda xatolik: {e}")
    
    def seed_data(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Admin
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ('admin', password, 'admin')
            )
            print("✅ Admin user created: admin / admin123")
        
        # Cashier
        cursor.execute("SELECT * FROM users WHERE username = 'cashier'")
        if not cursor.fetchone():
            password = bcrypt.hashpw("cashier123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ('cashier', password, 'cashier')
            )
            print("✅ Cashier user created: cashier / cashier123")
        
        # Shop settings
        cursor.execute("SELECT * FROM shop_settings")
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO shop_settings (shop_name, address, phone, receipt_footer)
                VALUES (?, ?, ?, ?)
            ''', ('Moy almashtirish', 'Toshkent sh., ...', '+998 99 123 45 67', 'Rahmat! Xush kelibsiz!'))
            print("✅ Shop settings created")
        
        # Employees
        cursor.execute("SELECT * FROM employees")
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO employees (full_name, phone, position, salary, hire_date)
                VALUES (?, ?, ?, ?, ?)
            ''', ('Admin', '+998 99 111 22 33', 'Admin', 0, '2024-01-01'))
            print("✅ Default employee created")
        
        # Test firm (agar bo'sh bo'lsa)
        cursor.execute("SELECT * FROM firms")
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO firms (name, phone, address, total_debt, note)
                VALUES (?, ?, ?, ?, ?)
            ''', ('Test firma', '+998 99 123 45 67', 'Toshkent sh.', 0, 'Test uchun'))
            print("✅ Test firma qo'shildi!")
        
        # Test categories
        cursor.execute("SELECT * FROM categories")
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO categories (name, icon, color)
                VALUES (?, ?, ?)
            ''', ('Moylar', '🛢️', '#FF6B6B'))
            cursor.execute('''
                INSERT INTO categories (name, icon, color)
                VALUES (?, ?, ?)
            ''', ('Filtrlari', '🔧', '#4ECDC4'))
            cursor.execute('''
                INSERT INTO categories (name, icon, color)
                VALUES (?, ?, ?)
            ''', ('Aksessuarlar', '🔩', '#45B7D1'))
            print("✅ Test kategoriyalar qo'shildi!")
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query, params=None):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                conn.close()
                if result:
                    return [dict(row) for row in result]
                return []
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return None
    
    def execute_query_one(self, query, params=None):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return dict(result)
            return None
            
        except Exception as e:
            print(f"❌ Database error (one): {e}")
            if conn:
                conn.close()
            return None

    def execute_insert(self, query, params=None):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
            
        except Exception as e:
            print(f"❌ Database insert error: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return None
    
    def execute_update(self, query, params=None):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            return affected_rows
            
        except Exception as e:
            print(f"❌ Database update error: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return -1