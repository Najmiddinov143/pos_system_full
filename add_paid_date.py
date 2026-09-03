# add_paid_date.py - YANGI FAYL (FAQAT paid_date QO'SHISH UCHUN)

import sqlite3
import os

def add_paid_date_column():
    db_path = "database/pos.db"
    
    if not os.path.exists(db_path):
        print("❌ Ma'lumotlar bazasi topilmadi!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. stock_purchases jadvaliga paid_date ustunini qo'shish
    try:
        cursor.execute("ALTER TABLE stock_purchases ADD COLUMN paid_date TEXT")
        print("✅ paid_date ustuni qo'shildi!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✅ paid_date ustuni allaqachon mavjud")
        else:
            print(f"⚠️ Xatolik: {e}")
    
    # 2. stock_purchases jadvaliga remaining_debt ustunini qo'shish
    try:
        cursor.execute("ALTER TABLE stock_purchases ADD COLUMN remaining_debt REAL DEFAULT 0")
        print("✅ remaining_debt ustuni qo'shildi!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✅ remaining_debt ustuni allaqachon mavjud")
        else:
            print(f"⚠️ Xatolik: {e}")
    
    conn.commit()
    conn.close()
    print("✅ Ma'lumotlar bazasi yangilandi!")

if __name__ == "__main__":
    add_paid_date_column()