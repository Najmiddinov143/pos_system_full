# database/migrations/create_firm_debts_table.py
import sqlite3
import os

def create_firm_debts_table():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect("database/pos.db")
    cursor = conn.cursor()
    
    # Firmalar qarzlari tarixi (mahsulotsiz qo'shilgan qarzlar)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS firm_debts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firm_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            debt_type TEXT DEFAULT 'qarz' CHECK(debt_type IN ('qarz', 'to_lov')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (firm_id) REFERENCES firms(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ firm_debts table yaratildi!")

if __name__ == "__main__":
    create_firm_debts_table()