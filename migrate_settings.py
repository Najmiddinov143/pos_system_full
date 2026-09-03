# migrate_settings.py
import sqlite3

def migrate():
    conn = sqlite3.connect("database/pos.db")
    cursor = conn.cursor()
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Default settings
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ('notification_enabled', 'true'))
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ('sound_enabled', 'true'))
    
    conn.commit()
    conn.close()
    print("✅ Settings table yaratildi!")

if __name__ == "__main__":
    migrate()