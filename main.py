import sys
import os
import threading
import sqlite3
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from views.login_window import LoginWindow
from telegram.error import BadRequest, TelegramError

# ===== YO'LNI ANIQLASH =====
def get_base_path():
    """Ishga tushirilgan papkani aniqlash (exe va py uchun)"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def get_db_path():
    """Ma'lumotlar bazasi yo'lini qaytaradi"""
    base_path = get_base_path()
    db_path = os.path.join(base_path, "database", "pos.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return db_path


# ===== MA'LUMOTLAR BAZASINI TEKSHIRISH =====
def check_and_fix_database():
    """Ma'lumotlar bazasini tekshirish va yangilash"""
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        print("⚠️ Ma'lumotlar bazasi topilmadi! Yangi yaratilmoqda...")
        try:
            from migrate_db import create_database
            create_database()
        except:
            print("❌ migrate_db topilmadi! Yangi baza yaratilmoqda...")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Users
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('admin', 'cashier')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Products
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Sales
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
                    customer_phone TEXT
                )
            ''')
            
            # Sale items
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity REAL NOT NULL,
                    sell_price REAL NOT NULL,
                    cost_price REAL NOT NULL,
                    subtotal REAL NOT NULL
                )
            ''')
            
            # Expenses
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    payment_type TEXT DEFAULT 'Naxt' CHECK(payment_type IN ('Naxt', 'Plastik')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER
                )
            ''')
            
            # Inventory logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER
                )
            ''')
            
            # Employees
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
            
            # Backup history
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
            
            # Notifications
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    type TEXT NOT NULL,
                    is_read INTEGER DEFAULT 0,
                    user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Shop settings
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
            
            # Attendance
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    check_in TEXT,
                    check_out TEXT,
                    date TEXT NOT NULL
                )
            ''')
            
            # Settings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Stock purchases
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Firms
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
            
            # Firm debts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS firm_debts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    firm_id INTEGER NOT NULL,
                    firm_name TEXT,
                    amount REAL NOT NULL,
                    description TEXT,
                    debt_type TEXT DEFAULT 'qarz' CHECK(debt_type IN ('qarz', 'to_lov')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            import bcrypt
            admin_pwd = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute('INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                           ('admin', admin_pwd, 'admin'))
            
            cashier_pwd = bcrypt.hashpw('cashier123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute('INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                           ('cashier', cashier_pwd, 'cashier'))
            
            cursor.execute('''
                INSERT OR IGNORE INTO shop_settings (shop_name, address, phone, receipt_footer)
                VALUES (?, ?, ?, ?)
            ''', ('Moy almashtirish', 'Toshkent sh., ...', '+998 99 123 45 67', 'Rahmat! Xush kelibsiz!'))
            
            conn.commit()
            conn.close()
            print("✅ Ma'lumotlar bazasi yaratildi!")
        return
    
    # Mavjud bazani tekshirish
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # stock_purchases jadvalidagi ustunlarni tekshirish
        cursor.execute("PRAGMA table_info(stock_purchases)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'remaining_debt' not in columns:
            try:
                cursor.execute("ALTER TABLE stock_purchases ADD COLUMN remaining_debt REAL DEFAULT 0")
                print("✅ remaining_debt ustuni qo'shildi!")
            except Exception as e:
                print(f"⚠️ remaining_debt qo'shishda xatolik: {e}")
        
        if 'paid_date' not in columns:
            try:
                cursor.execute("ALTER TABLE stock_purchases ADD COLUMN paid_date TEXT")
                print("✅ paid_date ustuni qo'shildi!")
            except Exception as e:
                print(f"⚠️ paid_date qo'shishda xatolik: {e}")
        
        # products jadvalida is_active ustuni
        cursor.execute("PRAGMA table_info(products)")
        product_columns = [col[1] for col in cursor.fetchall()]
        if 'is_active' not in product_columns:
            try:
                cursor.execute("ALTER TABLE products ADD COLUMN is_active INTEGER DEFAULT 1")
                print("✅ is_active ustuni qo'shildi!")
            except Exception as e:
                print(f"⚠️ is_active qo'shishda xatolik: {e}")
        
        # firms jadvali
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='firms'")
        if not cursor.fetchone():
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
            print("✅ firms table yaratildi!")
        
        # firm_debts jadvali
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("✅ firm_debts table yaratildi!")
        
        # firm_debts ga firm_name ustuni
        cursor.execute("PRAGMA table_info(firm_debts)")
        debt_columns = [col[1] for col in cursor.fetchall()]
        if 'firm_name' not in debt_columns:
            try:
                cursor.execute("ALTER TABLE firm_debts ADD COLUMN firm_name TEXT")
                print("✅ firm_debts ga firm_name ustuni qo'shildi!")
            except Exception as e:
                print(f"⚠️ firm_name qo'shishda xatolik: {e}")
        
        # expenses jadvaliga payment_type ustuni (Naxt/Plastik - qaysi kassadan yechilgani)
        cursor.execute("PRAGMA table_info(expenses)")
        expense_columns = [col[1] for col in cursor.fetchall()]
        if 'payment_type' not in expense_columns:
            try:
                cursor.execute("ALTER TABLE expenses ADD COLUMN payment_type TEXT DEFAULT 'Naxt'")
                print("✅ expenses ga payment_type ustuni qo'shildi!")
            except Exception as e:
                print(f"⚠️ payment_type qo'shishda xatolik: {e}")
        
        conn.commit()
        conn.close()
        print("✅ Ma'lumotlar bazasi tekshirildi!")
        
    except Exception as e:
        print(f"⚠️ Ma'lumotlar bazasini tekshirishda xatolik: {e}")

# ===== TELEGRAM BOT =====
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
    BOT_AVAILABLE = True
except ImportError:
    BOT_AVAILABLE = False
    print("⚠️ python-telegram-bot o'rnatilmagan! Bot ishlamaydi.")

BOT_TOKEN = "8520222825:AAE30r62L_RqRyymemJCifN_rEfULC2e2Ig"

from models.api_client import api


def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🔍 Qidirish", callback_data="search")],
        [InlineKeyboardButton("📦 Ombor holati", callback_data="inventory")],
        [InlineKeyboardButton("📊 Bugungi savdo", callback_data="today")],
        [InlineKeyboardButton("⚠️ Kam qolgan mahsulotlar", callback_data="low_stock")],
        [InlineKeyboardButton("🚗 Navbat", callback_data="queue")],
        [InlineKeyboardButton("🔐 Admin panel", callback_data="admin")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_menu():
    keyboard = [[InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)

def get_search_again_menu():
    keyboard = [
        [InlineKeyboardButton("🔍 Yana qidirish", callback_data="search")],
        [InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['awaiting_search'] = False
    welcome_text = (
        "🏪 *POS Tizimi Botiga xush kelibsiz!*\n\n"
        "📌 *Moy almashtirish ustalari uchun bot*\n"
        "⚡ Quyidagi tugmalardan birini tanlang:"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu(), parse_mode='Markdown')


# ============================================================
# 🌐 GLOBAL XATO-USHLAGICH
# ============================================================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"⚠️ Bot xatosi: {context.error}")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    try:
        await query.answer()
    except (BadRequest, TelegramError):
        pass
    except Exception as e:
        print(f"Callback javobida xatolik: {e}")

    try:
        if query.data == "main_menu":
            context.user_data["awaiting_search"] = False
            await show_main_menu(query)

        elif query.data == "search":
            await show_search_prompt(query, context)

        elif query.data == "inventory":
            await show_inventory(query)

        elif query.data == "today":
            await show_today_sales(query)

        elif query.data == "low_stock":
            await show_low_stock(query)

        elif query.data == "queue":
            await show_queue(query)

        elif query.data == "admin":
            await admin_panel(query)
    except (BadRequest, TelegramError) as e:
        print(f"⚠️ Telegram xatosi (button_handler): {e}")
    except Exception as e:
        print(f"❌ Kutilmagan xatolik (button_handler): {e}")

async def show_main_menu(query):
    welcome_text = (
        "🏪 *POS Tizimi Botiga xush kelibsiz!*\n\n"
        "📌 *Moy almashtirish ustalari uchun bot*\n"
        "⚡ Quyidagi tugmalardan birini tanlang:"
    )
    await query.edit_message_text(welcome_text, reply_markup=get_main_menu(), parse_mode='Markdown')


# ============================================================
# 🔍 QIDIRUV
# ============================================================
async def show_search_prompt(query, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['awaiting_search'] = True
    await query.edit_message_text(
        "🔍 *Mahsulot qidirish*\n\n"
        "📝 Qidirmoqchi bo'lgan mahsulot nomini yozib yuboring.\n"
        "Masalan: `Fosser` yoki `filter`\n\n"
        "_(To'liq nom yozish shart emas, bir qismini yozsangiz ham topadi)_",
        reply_markup=get_back_menu(),
        parse_mode='Markdown'
    )


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('awaiting_search'):
        return
    
    search_text = update.message.text.strip()
    context.user_data['awaiting_search'] = False
    
    if not search_text:
        await update.message.reply_text(
            "❌ Iltimos, mahsulot nomini yozing.",
            reply_markup=get_search_again_menu()
        )
        return
    
    try:
        products = api.get(f"/products/search/{search_text}") or []
        
        if not products:
            await update.message.reply_text(
                f"❌ *\"{search_text}\"* bo'yicha hech narsa topilmadi.\n\n"
                f"Boshqa nom bilan qayta urinib ko'ring.",
                reply_markup=get_search_again_menu(),
                parse_mode='Markdown'
            )
            return
        
        text = f"🔍 *QIDIRUV NATIJASI:* \"{search_text}\"\n"
        text += "═" * 30 + "\n\n"
        
        for p in products:
            qty = float(p.get('quantity', 0))
            min_qty = float(p.get('min_quantity', 5))
            status = "⚠️" if qty <= min_qty else "✅"
            text += f"{status} *{p.get('name', '')}*\n"
            text += f"   📊 Qoldiq: {qty} {p.get('unit', 'dona')}\n"
            text += f"   💰 Narx: {float(p.get('sell_price', 0)):,.0f} so'm\n"
            if p.get('category'):
                text += f"   🏷️ Kategoriya: {p['category']}\n"
            text += "\n"
        
        text += "═" * 30 + "\n"
        text += f"📋 Topildi: {len(products)} ta"
        
        await update.message.reply_text(
            text,
            reply_markup=get_search_again_menu(),
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Qidirishda xatolik: {str(e)}",
            reply_markup=get_search_again_menu()
        )


# ============================================================
# 📦 OMBOR HOLATI
# ============================================================
async def show_inventory(query):
    try:
        products = api.get("/products/") or []
        
        if not products:
            await query.edit_message_text("📦 Ombor bo'sh!", reply_markup=get_back_menu())
            return
        
        total_products = len(products)
        low_stock = sum(1 for p in products if float(p.get('quantity', 0)) <= float(p.get('min_quantity', 5)))
        
        text = "📦 *OMBOR HOLATI*\n"
        text += "═" * 30 + "\n\n"
        
        for p in products:
            qty = float(p.get('quantity', 0))
            min_qty = float(p.get('min_quantity', 5))
            status = "⚠️" if qty <= min_qty else "✅"
            text += f"{status} *{p.get('name', '')}*\n"
            text += f"   📊 {qty} {p.get('unit', 'dona')}"
            if qty <= min_qty:
                text += f" (min: {min_qty})"
            text += f"\n   💰 {float(p.get('sell_price', 0)):,.0f} so'm\n\n"
        
        text += "═" * 30 + "\n"
        text += f"📊 Jami: {total_products} ta\n"
        text += f"⚠️ Kam qolgan: {low_stock} ta"
        
        if len(text) > 4000:
            parts = []
            current_part = "📦 *OMBOR HOLATI* (1-qism)\n"
            current_part += "═" * 30 + "\n\n"
            part_num = 1
            
            for p in products:
                qty = float(p.get('quantity', 0))
                min_qty = float(p.get('min_quantity', 5))
                status = "⚠️" if qty <= min_qty else "✅"
                line = f"{status} *{p.get('name', '')}*\n"
                line += f"   📊 {qty} {p.get('unit', 'dona')}"
                if qty <= min_qty:
                    line += f" (min: {min_qty})"
                line += f"\n   💰 {float(p.get('sell_price', 0)):,.0f} so'm\n\n"
                
                if len(current_part) + len(line) > 3900:
                    current_part += f"\n📌 {part_num}-qism tugadi..."
                    parts.append(current_part)
                    part_num += 1
                    current_part = f"📦 *OMBOR HOLATI* ({part_num}-qism)\n"
                    current_part += "═" * 30 + "\n\n"
                
                current_part += line
            
            current_part += "\n" + "═" * 30 + "\n"
            current_part += f"📊 Jami: {total_products} ta\n"
            current_part += f"⚠️ Kam qolgan: {low_stock} ta"
            parts.append(current_part)
            
            await query.edit_message_text(parts[0], parse_mode='Markdown')
            for i in range(1, len(parts)):
                await query.message.reply_text(parts[i], parse_mode='Markdown')
            await query.message.reply_text("📌 Barcha mahsulotlar ko'rsatildi.", reply_markup=get_back_menu())
        else:
            await query.edit_message_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')
            
    except Exception as e:
        await query.edit_message_text(f"❌ Xatolik: {str(e)}", reply_markup=get_back_menu())


# ============================================================
# 📊 BUGUNGI SAVDO
# ============================================================
async def show_today_sales(query):
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        totals = api.get(f"/sales/totals/{today}") or {"total": 0, "count": 0, "profit": 0}
        last_sales = api.get(f"/sales/date/{today}") or []
        
        text = f"📊 *BUGUNGI SAVDO*\n"
        text += "═" * 30 + "\n"
        text += f"📅 Sana: {today}\n"
        text += f"💰 *Jami:* {float(totals.get('total', 0)):,.0f} so'm\n"
        text += f"📋 Sotuvlar: {totals.get('count', 0)} ta\n"
        text += f"💹 Foyda: {float(totals.get('profit', 0)):,.0f} so'm\n\n"
        
        if last_sales:
            text += "📋 *Oxirgi sotuvlar:*\n"
            text += "─" * 20 + "\n"
            for s in last_sales[:5]:
                created = s.get('created_at', '')
                time_str = created[11:16] if len(created) > 16 else ''
                text += f"#{s.get('id', '')} "
                text += f"🕐 {time_str} "
                text += f"💰 {float(s.get('total_amount', 0)):,.0f} so'm"
                if s.get('car_number'):
                    text += f"\n   🚗 {s['car_number']}"
                text += "\n"
        
        await query.edit_message_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')
    except Exception as e:
        await query.edit_message_text(f"❌ Xatolik: {str(e)}", reply_markup=get_back_menu())


# ============================================================
# ⚠️ KAM QOLGAN MAHSULOTLAR
# ============================================================
async def show_low_stock(query):
    try:
        products = api.get("/products/") or []
        low_stock = [p for p in products if float(p.get('quantity', 0)) <= float(p.get('min_quantity', 5))]
        
        if not low_stock:
            await query.edit_message_text("✅ Barcha mahsulotlar yetarli miqdorda!", reply_markup=get_back_menu())
            return
        
        text = "⚠️ *KAM QOLGAN MAHSULOTLAR*\n"
        text += "═" * 30 + "\n\n"
        
        for p in low_stock:
            qty = float(p.get('quantity', 0))
            min_qty = float(p.get('min_quantity', 5))
            text += f"🔴 *{p.get('name', '')}*\n"
            text += f"   📊 Qoldiq: {qty} {p.get('unit', 'dona')}\n"
            text += f"   📉 Minimal: {min_qty}\n\n"
        
        text += "═" * 30 + "\n"
        text += f"📋 Jami: {len(low_stock)} ta mahsulot kam qolgan"
        
        if len(text) > 4000:
            parts = []
            part_num = 1
            current_part = f"⚠️ *KAM QOLGAN MAHSULOTLAR* ({part_num}-qism)\n"
            current_part += "═" * 30 + "\n\n"
            
            for p in low_stock:
                qty = float(p.get('quantity', 0))
                min_qty = float(p.get('min_quantity', 5))
                line = f"🔴 *{p.get('name', '')}*\n"
                line += f"   📊 Qoldiq: {qty} {p.get('unit', 'dona')}\n"
                line += f"   📉 Minimal: {min_qty}\n\n"
                
                if len(current_part) + len(line) > 3900:
                    current_part += f"\n📌 {part_num}-qism tugadi..."
                    parts.append(current_part)
                    part_num += 1
                    current_part = f"⚠️ *KAM QOLGAN MAHSULOTLAR* ({part_num}-qism)\n"
                    current_part += "═" * 30 + "\n\n"
                
                current_part += line
            
            current_part += "\n" + "═" * 30 + "\n"
            current_part += f"📋 Jami: {len(low_stock)} ta mahsulot kam qolgan"
            parts.append(current_part)
            
            await query.edit_message_text(parts[0], parse_mode='Markdown')
            for i in range(1, len(parts)):
                await query.message.reply_text(parts[i], parse_mode='Markdown')
            await query.message.reply_text("📌 Barcha kam qolgan mahsulotlar ko'rsatildi.", reply_markup=get_back_menu())
        else:
            await query.edit_message_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')
            
    except Exception as e:
        await query.edit_message_text(f"❌ Xatolik: {str(e)}", reply_markup=get_back_menu())


# ============================================================
# 🚗 NAVBAT
# ============================================================
async def show_queue(query):
    try:
        queue = api.get("/sales/upcoming-notifications?days=3") or []
        
        if not queue:
            await query.edit_message_text(
                "✅ *Navbatda mijozlar yo'q!*\n\n"
                "🚗 Hozircha keladigan mijozlar yo'q.",
                reply_markup=get_back_menu(),
                parse_mode='Markdown'
            )
            return
        
        text = "🚗 *NAVBATDAGI MIJOZLAR*\n"
        text += "═" * 30 + "\n\n"
        
        for i, q in enumerate(queue[:20], 1):
            car_number = q.get('car_number') or "Noma'lum"
            text += f"*{i}. 🚗 {car_number}*\n"
            if q.get('car_model'):
                text += f"   📌 Model: {q['car_model']}\n"
            text += f"   📏 Joriy km: {float(q.get('current_km', 0)):,.0f} km\n"
            text += f"   📅 Keyingi moy: {q.get('next_oil_change_date', '')}\n"
            text += f"   💰 Summa: {float(q.get('total_amount', 0)):,.0f} so'm\n\n"
        
        text += "═" * 30 + "\n"
        text += f"📋 Jami: {len(queue)} ta mijoz navbatda"
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_menu(),
            parse_mode='Markdown'
        )
    except Exception as e:
        await query.edit_message_text(
            f"❌ Xatolik: {str(e)}",
            reply_markup=get_back_menu()
        )


# ============================================================
# 🔐 ADMIN PANEL
# ============================================================
async def admin_panel(query):
    await query.edit_message_text(
        "🔐 *Admin panel*\n\n"
        "📌 Barcha ma'lumotlarni ko'rish uchun parolni kiriting:\n"
        "`/password admin123`\n\n"
        "📌 Yoki quyidagi buyruqlarni ishlating:\n"
        "• `/stats` - Umumiy statistika\n"
        "• `/sales` - Oxirgi sotuvlar\n"
        "• `/qidir <nomi>` - Mahsulot qidirish",
        reply_markup=get_back_menu(),
        parse_mode='Markdown'
    )


async def password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        if text.startswith('/password '):
            password = text.replace('/password ', '').strip()
        else:
            await update.message.reply_text("❌ /password parol deb yozing")
            return
        
        if password == "admin123":
            await show_admin_stats(update)
        else:
            await update.message.reply_text("❌ Noto'g'ri parol!")
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")


async def show_admin_stats(update):
    try:
        dashboard = api.get("/reports/dashboard") or {}
        today = datetime.now().strftime('%Y-%m-%d')
        today_stats = api.get(f"/sales/totals/{today}") or {"total": 0, "count": 0}
        recent_sales = api.get("/sales/") or []
        
        text = "🔐 *ADMIN PANEL*\n"
        text += "═" * 30 + "\n\n"
        
        text += "📊 *UMUMIY STATISTIKA*\n"
        text += f"📦 Mahsulotlar: {dashboard.get('products_count', 0)}\n"
        text += f"💰 Tannarx: {float(dashboard.get('total_cost', 0)):,.0f} so'm\n"
        text += f"💵 Qiymat: {float(dashboard.get('total_value', 0)):,.0f} so'm\n"
        text += f"🏆 Jami foyda: {float(dashboard.get('total_profit', 0)):,.0f} so'm\n"
        text += f"📋 Jami sotuv: {dashboard.get('today_sales', 0)} ta\n\n"
        
        text += "📊 *BUGUNGI STATISTIKA*\n"
        text += f"💰 Savdo: {float(today_stats.get('total', 0)):,.0f} so'm\n"
        text += f"📋 Sotuv: {today_stats.get('count', 0)} ta\n\n"
        
        if recent_sales:
            text += "📋 *OXIRGI SOTUVLAR*\n"
            text += "─" * 20 + "\n"
            for s in recent_sales[:10]:
                created = s.get('created_at', '')
                date_str = created[:16] if len(created) > 16 else created
                text += f"#{s.get('id', '')} | {date_str} | "
                text += f"{float(s.get('total_amount', 0)):,.0f} so'm"
                if s.get('car_number'):
                    text += f" | 🚗 {s['car_number']}"
                text += "\n"
        
        await update.message.reply_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_admin_stats(update)


async def sales_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sales = api.get("/sales/") or []
        
        if not sales:
            await update.message.reply_text("📋 Sotuvlar yo'q!")
            return
        
        text = "📋 *OXIRGI SOTUVLAR*\n"
        text += "═" * 30 + "\n\n"
        
        for s in sales[:20]:
            created = s.get('created_at', '')
            time_str = created[:16] if len(created) > 16 else created
            text += f"#{s.get('id', '')} "
            text += f"🕐 {time_str}\n"
            text += f"💰 {float(s.get('total_amount', 0)):,.0f} so'm"
            if s.get('car_number'):
                text += f" | 🚗 {s['car_number']}"
            text += "\n\n"
        
        await update.message.reply_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")


# ===== /qidir buyrug'i =====
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    search_text = text.replace('/qidir', '', 1).strip()
    
    if not search_text:
        context.user_data['awaiting_search'] = True
        await update.message.reply_text(
            "🔍 Qidirmoqchi bo'lgan mahsulot nomini yozing:",
            reply_markup=get_back_menu()
        )
        return
    
    context.user_data['awaiting_search'] = True
    update.message.text = search_text
    await handle_text_message(update, context)


def run_bot():
    """Botni alohida threadda ishga tushirish (asyncio-safe)"""
    if not BOT_AVAILABLE:
        return

    import asyncio

    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        from telegram.request import HTTPXRequest

        request = HTTPXRequest(
            connect_timeout=30.0,
            read_timeout=30.0,
            write_timeout=30.0,
            pool_timeout=30.0,
        )

        app = Application.builder().token(BOT_TOKEN).request(request).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("password", password_handler))
        app.add_handler(CommandHandler("stats", stats_command))
        app.add_handler(CommandHandler("sales", sales_command))
        app.add_handler(CommandHandler("qidir", search_command))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

        app.add_error_handler(error_handler)

        # Use non-blocking lifecycle instead of run_polling()
        loop.run_until_complete(app.initialize())
        loop.run_until_complete(app.start())
        loop.run_until_complete(app.updater.start_polling(drop_pending_updates=True))

        print("=" * 50)
        print("🤖 Telegram bot ishga tushdi!")
        print("📱 Botni oching va /start yozing")
        print("=" * 50)

        # Keep the thread alive until process exits
        import time
        while True:
            time.sleep(1)

    except Exception as e:
        print(f"❌ Bot xatosi: {e}")
    finally:
        try:
            loop.run_until_complete(app.stop())
            loop.run_until_complete(app.shutdown())
        except:
            pass
        loop.close()


# ===== ASOSIY FUNKSIYA =====
def main():
    # Papkalarni yaratish
    os.makedirs("database", exist_ok=True)
    os.makedirs("assets/icons", exist_ok=True)
    os.makedirs("assets/product_images", exist_ok=True)
    os.makedirs("assets/sound", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    
    # Ma'lumotlar bazasini tekshirish
    check_and_fix_database()
    
    # Botni alohida threadda ishga tushirish
    if BOT_AVAILABLE:
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        print("✅ Bot thread ishga tushdi")
    else:
        print("⚠️ Bot o'chirilgan (python-telegram-bot o'rnatilmagan)")
    
    # GUI ni ishga tushirish
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName("POS Tizimi")
    app.setOrganizationName("POS System")
    
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
    