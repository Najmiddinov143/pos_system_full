# database/migrations/create_firms_table.py
import sqlite3
import os

def create_firms_table():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect("database/pos.db")
    cursor = conn.cursor()
    
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
    
    conn.commit()
    conn.close()
    print("✅ Firms table yaratildi!")

if __name__ == "__main__":
    create_firms_table()