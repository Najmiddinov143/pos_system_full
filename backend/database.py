# backend/database.py - PostgreSQL connection and schema

import os
import asyncpg
from contextlib import asynccontextmanager

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pos_user:pos_password@localhost:5432/pos_db"
)

# Synchronous connection for schema creation
def get_sync_connection():
    import psycopg2
    return psycopg2.connect(DATABASE_URL)


async def create_pool():
    return await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)


async def init_db(pool: asyncpg.Pool):
    """Create all tables in PostgreSQL."""
    async with pool.acquire() as conn:
        await conn.execute("""
            -- 1. USERS
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role VARCHAR(20) NOT NULL CHECK(role IN ('admin', 'cashier')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- 17. CATEGORIES (created before products for FK)
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                parent_id INTEGER REFERENCES categories(id),
                icon TEXT,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- 15. FIRMS (created before stock_purchases for FK)
            CREATE TABLE IF NOT EXISTS firms (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                total_debt NUMERIC DEFAULT 0,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- 2. PRODUCTS
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                cost_price NUMERIC NOT NULL DEFAULT 0,
                sell_price NUMERIC NOT NULL DEFAULT 0,
                quantity NUMERIC NOT NULL DEFAULT 0,
                unit TEXT DEFAULT 'dona',
                min_quantity NUMERIC DEFAULT 5,
                note TEXT,
                image_path TEXT,
                barcode TEXT,
                supplier TEXT,
                is_active INTEGER DEFAULT 1,
                dollar_cost NUMERIC DEFAULT 0,
                dollar_price NUMERIC DEFAULT 0,
                exchange_rate NUMERIC DEFAULT 0,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- 3. SALES
            CREATE TABLE IF NOT EXISTS sales (
                id SERIAL PRIMARY KEY,
                total_amount NUMERIC NOT NULL DEFAULT 0,
                total_profit NUMERIC NOT NULL DEFAULT 0,
                discount NUMERIC DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER REFERENCES users(id),
                car_number TEXT,
                car_model TEXT,
                phone_number TEXT,
                current_km NUMERIC DEFAULT 0,
                next_km NUMERIC DEFAULT 0,
                oil_change_date TEXT,
                next_oil_change_date TEXT,
                notification_date TEXT,
                is_notified INTEGER DEFAULT 0,
                payment_type TEXT DEFAULT 'Naxt',
                bonus_amount NUMERIC DEFAULT 0,
                discount_amount NUMERIC DEFAULT 0,
                cash_amount NUMERIC DEFAULT 0,
                card_amount NUMERIC DEFAULT 0,
                extra_charge NUMERIC DEFAULT 0,
                is_debt INTEGER DEFAULT 0,
                debt_paid INTEGER DEFAULT 0,
                customer_name TEXT,
                customer_phone TEXT
            );

            -- 4. SALE ITEMS
            CREATE TABLE IF NOT EXISTS sale_items (
                id SERIAL PRIMARY KEY,
                sale_id INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
                product_id INTEGER NOT NULL REFERENCES products(id),
                quantity NUMERIC NOT NULL,
                sell_price NUMERIC NOT NULL,
                cost_price NUMERIC NOT NULL,
                subtotal NUMERIC NOT NULL
            );

            -- 5. EXPENSES
            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                amount NUMERIC NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                payment_type TEXT DEFAULT 'Naxt',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER REFERENCES users(id)
            );

            -- 6. INVENTORY LOGS
            CREATE TABLE IF NOT EXISTS inventory_logs (
                id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL REFERENCES products(id),
                action TEXT NOT NULL,
                quantity NUMERIC NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER REFERENCES users(id)
            );

            -- 7. EMPLOYEES
            CREATE TABLE IF NOT EXISTS employees (
                id SERIAL PRIMARY KEY,
                full_name TEXT NOT NULL,
                phone TEXT,
                position TEXT NOT NULL,
                salary NUMERIC DEFAULT 0,
                hire_date TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- 8. BACKUP HISTORY
            CREATE TABLE IF NOT EXISTS backup_history (
                id SERIAL PRIMARY KEY,
                backup_date TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_size INTEGER,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- 9. NOTIFICATIONS
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT DEFAULT 'Eslatma',
                is_read INTEGER DEFAULT 0,
                user_id INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- 10. SHOP SETTINGS
            CREATE TABLE IF NOT EXISTS shop_settings (
                id SERIAL PRIMARY KEY,
                shop_name TEXT NOT NULL DEFAULT 'Moy almashtirish',
                address TEXT,
                phone TEXT,
                logo_path TEXT,
                receipt_footer TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- 11. ATTENDANCE
            CREATE TABLE IF NOT EXISTS attendance (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER NOT NULL REFERENCES employees(id),
                check_in TEXT,
                check_out TEXT,
                date TEXT NOT NULL
            );

            -- 12. SETTINGS
            CREATE TABLE IF NOT EXISTS settings (
                id SERIAL PRIMARY KEY,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- 13. STOCK PURCHASES
            CREATE TABLE IF NOT EXISTS stock_purchases (
                id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL REFERENCES products(id),
                product_name TEXT,
                quantity NUMERIC NOT NULL,
                unit_cost NUMERIC NOT NULL,
                total_cost NUMERIC NOT NULL,
                dollar_cost NUMERIC DEFAULT 0,
                dollar_price NUMERIC DEFAULT 0,
                exchange_rate NUMERIC DEFAULT 0,
                payment_type TEXT DEFAULT 'Naxt' CHECK(payment_type IN ('Naxt', 'Nasiya')),
                purchase_date TEXT NOT NULL,
                due_date TEXT,
                is_paid INTEGER DEFAULT 0,
                paid_date TEXT,
                remaining_debt NUMERIC DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                firm_id INTEGER REFERENCES firms(id)
            );

            -- 14. CASH INCOMES
            CREATE TABLE IF NOT EXISTS cash_incomes (
                id SERIAL PRIMARY KEY,
                amount NUMERIC NOT NULL,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER REFERENCES users(id)
            );

            -- 16. FIRM DEBTS
            CREATE TABLE IF NOT EXISTS firm_debts (
                id SERIAL PRIMARY KEY,
                firm_id INTEGER NOT NULL REFERENCES firms(id),
                firm_name TEXT,
                amount NUMERIC NOT NULL,
                description TEXT,
                debt_type TEXT DEFAULT 'qarz' CHECK(debt_type IN ('qarz', 'to_lov')),
                is_paid INTEGER DEFAULT 0,
                paid_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- 18. DEBT PAYMENTS
            CREATE TABLE IF NOT EXISTS debt_payments (
                id SERIAL PRIMARY KEY,
                purchase_id INTEGER NOT NULL REFERENCES stock_purchases(id),
                paid_amount NUMERIC NOT NULL DEFAULT 0,
                cash_amount NUMERIC NOT NULL DEFAULT 0,
                card_amount NUMERIC NOT NULL DEFAULT 0,
                payment_type TEXT DEFAULT 'Naxt',
                paid_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- 19. FIRM DEBT PAYMENTS (already handled above)
            CREATE TABLE IF NOT EXISTS firm_debt_payments (
                id SERIAL PRIMARY KEY,
                debt_id INTEGER NOT NULL REFERENCES firm_debts(id),
                paid_amount NUMERIC NOT NULL DEFAULT 0,
                cash_amount NUMERIC NOT NULL DEFAULT 0,
                card_amount NUMERIC NOT NULL DEFAULT 0,
                payment_type TEXT DEFAULT 'Naxt',
                paid_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Seed default data
        import bcrypt
        admin_exists = await conn.fetchval("SELECT EXISTS(SELECT 1 FROM users WHERE username='admin')")
        if not admin_exists:
            pwd = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode("utf-8")
            await conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES ($1, $2, $3)",
                "admin", pwd, "admin"
            )

        cashier_exists = await conn.fetchval("SELECT EXISTS(SELECT 1 FROM users WHERE username='cashier')")
        if not cashier_exists:
            pwd = bcrypt.hashpw(b"cashier123", bcrypt.gensalt()).decode("utf-8")
            await conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES ($1, $2, $3)",
                "cashier", pwd, "cashier"
            )

        settings_exists = await conn.fetchval("SELECT EXISTS(SELECT 1 FROM shop_settings)")
        if not settings_exists:
            await conn.execute(
                """INSERT INTO shop_settings (shop_name, address, phone, receipt_footer)
                   VALUES ($1, $2, $3, $4)""",
                "Moy almashtirish", "Toshkent sh., ...",
                "+998 99 123 45 67", "Rahmat! Xush kelibsiz!"
            )

        cats_exists = await conn.fetchval("SELECT EXISTS(SELECT 1 FROM categories)")
        if not cats_exists:
            await conn.execute(
                "INSERT INTO categories (name, icon, color) VALUES ($1, $2, $3)",
                "Moylar", "🛢️", "#FF6B6B"
            )
            await conn.execute(
                "INSERT INTO categories (name, icon, color) VALUES ($1, $2, $3)",
                "Filtrlari", "🔧", "#4ECDC4"
            )
            await conn.execute(
                "INSERT INTO categories (name, icon, color) VALUES ($1, $2, $3)",
                "Aksessuarlar", "🔩", "#45B7D1"
            )

        firms_exists = await conn.fetchval("SELECT EXISTS(SELECT 1 FROM firms)")
        if not firms_exists:
            await conn.execute(
                "INSERT INTO firms (name, phone, address, total_debt, note) VALUES ($1, $2, $3, $4, $5)",
                "Test firma", "+998 99 123 45 67", "Toshkent sh.", 0, "Test uchun"
            )

        employees_exists = await conn.fetchval("SELECT EXISTS(SELECT 1 FROM employees)")
        if not employees_exists:
            await conn.execute(
                "INSERT INTO employees (full_name, phone, position, salary, hire_date) VALUES ($1, $2, $3, $4, $5)",
                "Admin", "+998 99 111 22 33", "Admin", 0, "2024-01-01"
            )

    print("✅ Database schema created and seeded!")


def row_to_dict(row):
    """Convert asyncpg Record to dict."""
    if row is None:
        return None
    return dict(row)


def rows_to_dicts(rows):
    """Convert list of asyncpg Records to list of dicts."""
    return [dict(r) for r in rows]
