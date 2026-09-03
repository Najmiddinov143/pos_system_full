# migrate_phone.py
import sqlite3

def add_phone_column():
    conn = sqlite3.connect("database/pos.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE sales ADD COLUMN phone_number TEXT")
        print("✅ phone_number ustuni qo'shildi!")
    except sqlite3.OperationalError as e:
        print(f"⚠️ Xatolik: {e}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_phone_column()