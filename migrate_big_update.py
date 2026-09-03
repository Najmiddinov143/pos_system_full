# migrate_big_update.py
import sqlite3
import os

def migrate():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect("database/pos.db")
    cursor = conn.cursor()
    
    # Sales table borligini tekshirish
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales'")
    if cursor.fetchone():
        print("✅ Sales table mavjud, yangi ustunlar qo'shilmoqda...")
        
        # Yangi ustunlar
        columns = [
            ('payment_type', 'TEXT DEFAULT "Naxt"'),
            ('discount_amount', 'REAL DEFAULT 0'),
            ('bonus_amount', 'REAL DEFAULT 0'),
            ('is_debt', 'INTEGER DEFAULT 0'),
            ('debt_paid', 'INTEGER DEFAULT 0'),
            ('customer_name', 'TEXT'),
            ('customer_phone', 'TEXT')
        ]
        
        for col_name, col_type in columns:
            try:
                cursor.execute(f"ALTER TABLE sales ADD COLUMN {col_name} {col_type}")
                print(f"✅ {col_name} ustuni qo'shildi!")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"⚠️ {col_name} ustuni allaqachon mavjud")
                else:
                    print(f"⚠️ Xatolik: {e}")
    else:
        print("❌ Sales table mavjud emas! Avval dasturni ishga tushiring.")
    
    # Debts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS debts (
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
    
    conn.commit()
    conn.close()
    print("✅ Migratsiya tugadi!")

if __name__ == "__main__":
    migrate()