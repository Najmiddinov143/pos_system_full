# bot_main.py - TO'LIQ TUZATILGAN
import sqlite3
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ===== TOKEN =====
BOT_TOKEN = "8520222825:AAE30r62L_RqRyymemJCifN_rEfULC2e2Ig"

DB_PATH = "database/pos.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_main_menu():
    keyboard = [
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🏪 *POS Tizimi Botiga xush kelibsiz!*\n\n"
        "📌 *Moy almashtirish ustalari uchun bot*\n"
        "⚡ Quyidagi tugmalardan birini tanlang:"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu(), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "main_menu":
        await show_main_menu(query)
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

async def show_main_menu(query):
    welcome_text = (
        "🏪 *POS Tizimi Botiga xush kelibsiz!*\n\n"
        "📌 *Moy almashtirish ustalari uchun bot*\n"
        "⚡ Quyidagi tugmalardan birini tanlang:"
    )
    await query.edit_message_text(welcome_text, reply_markup=get_main_menu(), parse_mode='Markdown')

# bot_main.py - show_inventory ga qo'shing

async def show_inventory(query):
    try:
        conn = get_db()
        products = conn.execute('SELECT * FROM products ORDER BY name').fetchall()
        conn.close()
        
        if not products:
            await query.edit_message_text("📦 Ombor bo'sh!", reply_markup=get_back_menu())
            return
        
        # Rasm bilan yuborish
        for p in products[:3]:  # 3 tasini rasm bilan yuborish
            try:
                # Rasm yo'lini tekshirish
                image_path = p.get('image_path')
                if image_path and os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        await query.message.reply_photo(
                            photo=f,
                            caption=f"📦 *{p['name']}*\n"
                                   f"💰 {p['sell_price']:,.0f} so'm\n"
                                   f"📊 {p['quantity']} {p['unit']}"
                        )
                else:
                    # Rasm yo'q bo'lsa matn bilan yuborish
                    text = f"📦 *{p['name']}*\n"
                    text += f"💰 {p['sell_price']:,.0f} so'm\n"
                    text += f"📊 {p['quantity']} {p['unit']}"
                    await query.message.reply_text(text, parse_mode='Markdown')
            except:
                pass
        
        await query.edit_message_text("📦 Yuqorida mahsulotlar ro'yxati...", reply_markup=get_back_menu())
        
    except Exception as e:
        await query.edit_message_text(f"❌ Xatolik: {str(e)}", reply_markup=get_back_menu())
        
    try:
        conn = get_db()
        products = conn.execute('SELECT * FROM products ORDER BY name').fetchall()
        conn.close()
        
        if not products:
            await query.edit_message_text("📦 Ombor bo'sh!", reply_markup=get_back_menu())
            return
        
        text = "📦 *OMBOR HOLATI*\n"
        text += "═" * 30 + "\n\n"
        
        count = 0
        for p in products:
            status = "⚠️" if p['quantity'] <= p['min_quantity'] else "✅"
            text += f"{status} *{p['name']}*\n"
            text += f"   📊 {p['quantity']} {p['unit']}"
            if p['quantity'] <= p['min_quantity']:
                text += f" (min: {p['min_quantity']})"
            text += f"\n   💰 {p['sell_price']:,.0f} so'm\n\n"
            count += 1
            if count >= 20:
                text += f"📌 ... va yana {len(products)-20} ta mahsulot"
                break
        
        conn = get_db()
        total_products = conn.execute('SELECT COUNT(*) as count FROM products').fetchone()['count']
        low_stock = conn.execute('SELECT COUNT(*) as count FROM products WHERE quantity <= min_quantity').fetchone()['count']
        conn.close()
        
        text += "\n" + "═" * 30 + "\n"
        text += f"📊 Jami: {total_products} ta\n"
        text += f"⚠️ Kam qolgan: {low_stock} ta"
        
        await query.edit_message_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')
    except Exception as e:
        await query.edit_message_text(f"❌ Xatolik: {str(e)}", reply_markup=get_back_menu())

async def show_today_sales(query):
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        conn = get_db()
        sales = conn.execute('''
            SELECT 
                COALESCE(SUM(total_amount), 0) as total,
                COALESCE(COUNT(*), 0) as count,
                COALESCE(SUM(total_profit), 0) as profit
            FROM sales 
            WHERE DATE(created_at) = ?
        ''', (today,)).fetchone()
        
        last_sales = conn.execute('''
            SELECT * FROM sales 
            WHERE DATE(created_at) = ?
            ORDER BY created_at DESC
            LIMIT 5
        ''', (today,)).fetchall()
        conn.close()
        
        text = f"📊 *BUGUNGI SAVDO*\n"
        text += "═" * 30 + "\n"
        text += f"📅 Sana: {today}\n"
        text += f"💰 *Jami:* {sales['total']:,.0f} so'm\n"
        text += f"📋 Sotuvlar: {sales['count']} ta\n"
        text += f"💹 Foyda: {sales['profit']:,.0f} so'm\n\n"
        
        if last_sales:
            text += "📋 *Oxirgi sotuvlar:*\n"
            text += "─" * 20 + "\n"
            for s in last_sales:
                text += f"#{s['id']} "
                text += f"🕐 {s['created_at'][11:16]} "
                text += f"💰 {s['total_amount']:,.0f} so'm"
                if s['car_number']:
                    text += f"\n   🚗 {s['car_number']}"
                text += "\n"
        
        await query.edit_message_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')
    except Exception as e:
        await query.edit_message_text(f"❌ Xatolik: {str(e)}", reply_markup=get_back_menu())

async def show_low_stock(query):
    try:
        conn = get_db()
        products = conn.execute('''
            SELECT * FROM products 
            WHERE quantity <= min_quantity 
            ORDER BY quantity ASC
        ''').fetchall()
        conn.close()
        
        if not products:
            await query.edit_message_text("✅ Barcha mahsulotlar yetarli miqdorda!", reply_markup=get_back_menu())
            return
        
        text = "⚠️ *KAM QOLGAN MAHSULOTLAR*\n"
        text += "═" * 30 + "\n\n"
        
        for p in products:
            text += f"🔴 *{p['name']}*\n"
            text += f"   📊 Qoldiq: {p['quantity']} {p['unit']}\n"
            text += f"   📉 Minimal: {p['min_quantity']}\n\n"
        
        await query.edit_message_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')
    except Exception as e:
        await query.edit_message_text(f"❌ Xatolik: {str(e)}", reply_markup=get_back_menu())

async def show_queue(query):
    """Navbatdagi mijozlar - 3 kun ichida kelishi kerak bo'lganlar"""
    try:
        today = datetime.now().date()
        start_date = today
        end_date = today + timedelta(days=3)
        
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        conn = get_db()
        queue = conn.execute('''
            SELECT s.*, u.username 
            FROM sales s
            LEFT JOIN users u ON s.user_id = u.id
            WHERE DATE(s.next_oil_change_date) BETWEEN DATE(?) AND DATE(?)
            AND s.is_notified = 0
            ORDER BY s.next_oil_change_date ASC, s.created_at ASC
            LIMIT 20
        ''', (start_date_str, end_date_str)).fetchall()
        conn.close()
        
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
        
        for i, q in enumerate(queue, 1):
            car_number = q['car_number'] or "Noma'lum"
            text += f"*{i}. 🚗 {car_number}*\n"
            if q['car_model']:
                text += f"   📌 Model: {q['car_model']}\n"
            text += f"   📏 Joriy km: {q['current_km']:,.0f} km\n"
            text += f"   📅 Keyingi moy: {q['next_oil_change_date']}\n"
            text += f"   💰 Summa: {q['total_amount']:,.0f} so'm\n\n"
        
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

async def admin_panel(query):
    await query.edit_message_text(
        "🔐 *Admin panel*\n\n"
        "📌 Barcha ma'lumotlarni ko'rish uchun parolni kiriting:\n"
        "`/password admin123`\n\n"
        "📌 Yoki quyidagi buyruqlarni ishlating:\n"
        "• `/stats` - Umumiy statistika\n"
        "• `/sales` - Oxirgi sotuvlar",
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
        conn = get_db()
        
        stats = conn.execute('''
            SELECT 
                (SELECT COUNT(*) FROM products) as products,
                (SELECT COALESCE(SUM(cost_price * quantity), 0) FROM products) as total_cost,
                (SELECT COALESCE(SUM(sell_price * quantity), 0) FROM products) as total_value,
                (SELECT COALESCE(SUM(total_profit), 0) FROM sales) as total_profit,
                (SELECT COALESCE(COUNT(*), 0) FROM sales) as total_sales
        ''').fetchone()
        
        today = datetime.now().strftime('%Y-%m-%d')
        today_stats = conn.execute('''
            SELECT 
                COALESCE(SUM(total_amount), 0) as total,
                COALESCE(COUNT(*), 0) as count
            FROM sales WHERE DATE(created_at) = ?
        ''', (today,)).fetchone()
        
        sales = conn.execute('''
            SELECT * FROM sales 
            ORDER BY created_at DESC 
            LIMIT 10
        ''').fetchall()
        
        conn.close()
        
        text = "🔐 *ADMIN PANEL*\n"
        text += "═" * 30 + "\n\n"
        
        text += "📊 *UMUMIY STATISTIKA*\n"
        text += f"📦 Mahsulotlar: {stats['products']}\n"
        text += f"💰 Tannarx: {stats['total_cost']:,.0f} so'm\n"
        text += f"💵 Qiymat: {stats['total_value']:,.0f} so'm\n"
        text += f"🏆 Jami foyda: {stats['total_profit']:,.0f} so'm\n"
        text += f"📋 Jami sotuv: {stats['total_sales']} ta\n\n"
        
        text += "📊 *BUGUNGI STATISTIKA*\n"
        text += f"💰 Savdo: {today_stats['total']:,.0f} so'm\n"
        text += f"📋 Sotuv: {today_stats['count']} ta\n\n"
        
        if sales:
            text += "📋 *OXIRGI SOTUVLAR*\n"
            text += "─" * 20 + "\n"
            for s in sales:
                text += f"#{s['id']} | {s['created_at'][:16]} | "
                text += f"{s['total_amount']:,.0f} so'm"
                if s['car_number']:
                    text += f" | 🚗 {s['car_number']}"
                text += "\n"
        
        await update.message.reply_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_admin_stats(update)

async def sales_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = get_db()
        sales = conn.execute('''
            SELECT * FROM sales 
            ORDER BY created_at DESC 
            LIMIT 20
        ''').fetchall()
        conn.close()
        
        if not sales:
            await update.message.reply_text("📋 Sotuvlar yo'q!")
            return
        
        text = "📋 *OXIRGI SOTUVLAR*\n"
        text += "═" * 30 + "\n\n"
        
        for s in sales:
            text += f"#{s['id']} "
            text += f"🕐 {s['created_at'][:16]}\n"
            text += f"💰 {s['total_amount']:,.0f} so'm"
            if s['car_number']:
                text += f" | 🚗 {s['car_number']}"
            text += "\n\n"
        
        await update.message.reply_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("password", password_handler))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("sales", sales_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("=" * 50)
    print("🤖 POS Tizimi Bot ishga tushdi!")
    print("📱 Telegram da bot ni oching va /start yozing")
    print("=" * 50)
    
    app.run_polling()

if __name__ == "__main__":
    main()