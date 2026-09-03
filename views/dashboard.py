# views/dashboard.py - TO'LIQ TUZATILGAN

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils.styles import DARK_STYLE
from controllers.report_controller import ReportController
from controllers.expense_controller import ExpenseController
from controllers.product_controller import ProductController
from models.repositories import SaleRepository, ExpenseRepository, PurchaseRepository, IncomeRepository
from datetime import datetime, timedelta
import calendar

class Dashboard(QWidget):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.report_controller = ReportController()
        self.expense_controller = ExpenseController()
        self.product_controller = ProductController()
        self.sale_repo = SaleRepository()
        self.expense_repo = ExpenseRepository()
        self.purchase_repo = PurchaseRepository()
        self.income_repo = IncomeRepository()
        
        self.current_date = QDate.currentDate()
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.load_data()
    
    def showEvent(self, event):
        """Dashboard sahifasi har safar ko'rinar ekan (masalan boshqa sahifadan
        qaytilganda) ma'lumotlarni avtomatik yangilaydi. Aks holda, masalan
        Ombordan qarz to'langanda yoki yangi sotuv qilinganda, Dashboard
        eski (yangilanmagan) raqamlarni ko'rsatib turaverar edi."""
        super().showEvent(event)
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_widget = QWidget()
        header_widget.setFixedHeight(70)
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #1a1a2e, stop: 1 #2a2a4a);
                border-radius: 15px;
                padding: 15px;
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        title = QLabel("📊 Dashboard")
        title.setObjectName("titleLabel")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        date_layout = QHBoxLayout()
        
        prev_btn = QPushButton("◀")
        prev_btn.setObjectName("primaryButton")
        prev_btn.setFixedSize(35, 35)
        prev_btn.clicked.connect(self.prev_day)
        date_layout.addWidget(prev_btn)
        
        self.date_label = QLabel()
        self.date_label.setStyleSheet("""
            color: #e0e0e0;
            font-size: 16px;
            font-weight: bold;
            padding: 5px 20px;
            background: #14142a;
            border: 2px solid #2a2a4a;
            border-radius: 8px;
            min-width: 120px;
        """)
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_layout.addWidget(self.date_label)
        
        next_btn = QPushButton("▶")
        next_btn.setObjectName("primaryButton")
        next_btn.setFixedSize(35, 35)
        next_btn.clicked.connect(self.next_day)
        date_layout.addWidget(next_btn)
        
        today_btn = QPushButton("📅 Bugun")
        today_btn.setObjectName("primaryButton")
        today_btn.setMinimumHeight(35)
        today_btn.clicked.connect(self.go_today)
        date_layout.addWidget(today_btn)
        
        header_layout.addLayout(date_layout)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.setFixedSize(35, 35)
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn)
        
        layout.addWidget(header_widget)
        
        self.stats_layout = QGridLayout()
        self.stats_layout.setSpacing(15)
        layout.addLayout(self.stats_layout)
        
        if self.user and self.user.role == 'cashier':
            stats_row1 = [
                ('📈', 'Bugungi savdo', 'today_sales', '0 so\'m', 'cardOrange'),
                ('💰', 'Jami xarajat', 'total_expense', '0 so\'m', 'cardRed'),
                ('🎁', 'Bonus/Chegirma', 'bonus_total', '0 so\'m', 'cardOrange'),
                ('💎', 'Sof foyda', 'net_profit', '0 so\'m', 'cardGreen'),
            ]
            
            stats_row2 = [
                ('💵', 'Naxt savdo', 'cash_sales', '0 so\'m', 'cardBlue'),
                ('💳', 'Plastik savdo', 'card_sales', '0 so\'m', 'cardPurple'),
                ('📝', 'Nasiya savdo', 'debt_sales', '0 so\'m', 'cardOrange'),
            ]
            
            self.cards = {}
            row = 0
            
            for col, (icon, title, key, default, color) in enumerate(stats_row1):
                card = self.create_stat_card(icon, title, default, color)
                self.stats_layout.addWidget(card, row, col)
                self.cards[key] = card
            
            row = 1
            for col, (icon, title, key, default, color) in enumerate(stats_row2):
                card = self.create_stat_card(icon, title, default, color)
                self.stats_layout.addWidget(card, row, col)
                self.cards[key] = card
            
            row = 2
            balance_row = self.create_balance_row()
            self.stats_layout.addWidget(balance_row, row, 0, 1, 4)
            
        else:
            stats_row1 = [
                ('📦', 'Mahsulotlar soni', 'products_count', '0', 'cardBlue'),
                ('💰', 'Umumiy tannarx', 'total_cost', '0 so\'m', 'cardRed'),
                ('💵', 'Umumiy sotuv qiymati', 'total_value', '0 so\'m', 'cardGreen'),
                ('📈', 'Bugungi savdo', 'today_sales', '0 so\'m', 'cardOrange'),
            ]
            
            stats_row2 = [
                ('💹', 'Bugungi foyda', 'today_profit', '0 so\'m', 'cardPurple'),
                ('💰', 'Jami xarajat', 'total_expense', '0 so\'m', 'cardRed'),
                ('🎁', 'Bonus/Chegirma', 'bonus_total', '0 so\'m', 'cardOrange'),
                ('💎', 'Sof foyda', 'net_profit', '0 so\'m', 'cardGreen'),
            ]
            
            stats_row3 = [
                ('💵', 'Naxt savdo', 'cash_sales', '0 so\'m', 'cardBlue'),
                ('💳', 'Plastik savdo', 'card_sales', '0 so\'m', 'cardPurple'),
                ('📝', 'Nasiya savdo', 'debt_sales', '0 so\'m', 'cardOrange'),
                ('🏆', 'Jami foyda', 'total_profit', '0 so\'m', 'cardTeal'),
            ]
            
            self.cards = {}
            row = 0
            
            for col, (icon, title, key, default, color) in enumerate(stats_row1):
                card = self.create_stat_card(icon, title, default, color)
                self.stats_layout.addWidget(card, row, col)
                self.cards[key] = card
            
            row = 1
            for col, (icon, title, key, default, color) in enumerate(stats_row2):
                card = self.create_stat_card(icon, title, default, color)
                self.stats_layout.addWidget(card, row, col)
                self.cards[key] = card
            
            row = 2
            for col, (icon, title, key, default, color) in enumerate(stats_row3):
                card = self.create_stat_card(icon, title, default, color)
                self.stats_layout.addWidget(card, row, col)
                self.cards[key] = card
            
            row = 3
            balance_row = self.create_balance_row()
            self.stats_layout.addWidget(balance_row, row, 0, 1, 4)
        
        top_products_group = QGroupBox("🏆 Eng ko'p sotilgan mahsulotlar")
        top_products_group.setStyleSheet("""
            QGroupBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 12px;
                padding: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                color: #a0a0b8;
                font-weight: bold;
                padding: 0 10px;
                font-size: 16px;
            }
        """)
        top_products_layout = QVBoxLayout(top_products_group)
        
        self.top_products_table = QTableWidget()
        self.top_products_table.setColumnCount(4)
        self.top_products_table.setHorizontalHeaderLabels([
            '№', 'Mahsulot nomi', 'Sotilgan miqdor', 'Jami summa'
        ])
        self.top_products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.top_products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.top_products_table.horizontalHeader().setStretchLastSection(True)
        self.top_products_table.setStyleSheet("""
            QTableWidget {
                background: #1a1a2e;
                border: none;
                border-radius: 8px;
            }
            QHeaderView::section {
                background: #1a1a32;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #2a2a4a;
                color: #a0a0b8;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
                color: #e0e0e0;
            }
            QTableWidget::item:selected {
                background: #4a4a8a;
                color: white;
            }
        """)
        self.top_products_table.verticalHeader().setDefaultSectionSize(40)
        self.top_products_table.setMaximumHeight(250)
        top_products_layout.addWidget(self.top_products_table)
        
        layout.addWidget(top_products_group)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_data)
        self.timer.start(30000)
    
    def create_balance_row(self):
        """'Bugungi qoldiq' (naqd) va 'Plastik qoldiq' (karta) kartalari +
        'Kirim qo'shish' tugmasini bitta qatorda joylashtiradi.
        Naxt xarajatlar naqd qoldiqdan, Plastik xarajatlar esa karta
        qoldig'idan avtomatik kamayadi (Xarajatlar bo'limidagi to'lov turiga qarab)."""
        container = QWidget()
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(10)
        
        card = self.create_stat_card("💰", "Bugungi qoldiq (naqd)", "0 so'm", "cardTeal")
        card.setFixedHeight(120)
        self.cards['today_balance'] = card
        h_layout.addWidget(card, 1)
        
        card_balance_widget = self.create_stat_card("💳", "Plastik qoldiq", "0 so'm", "cardPurple")
        card_balance_widget.setFixedHeight(120)
        self.cards['card_balance'] = card_balance_widget
        h_layout.addWidget(card_balance_widget, 1)
        
        income_btn = QPushButton("➕\nKirim\nqo'shish")
        income_btn.setFixedHeight(120)
        income_btn.setFixedWidth(140)
        income_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        income_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #6c63ff, stop: 1 #4a42d4);
                color: white;
                font-weight: bold;
                font-size: 13px;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #7d74ff, stop: 1 #5b52e5);
            }
        """)
        income_btn.clicked.connect(self.add_income)
        h_layout.addWidget(income_btn)
        
        return container
    
    def add_income(self):
        """Savdo bilan bog'liq bo'lmagan naqd kirim qo'shish (masalan eski qarz qaytarilishi).
        Bu FOYDA hisoblanmaydi, faqat 'Bugungi qoldiq'ga qo'shiladi."""
        dialog = QDialog(self)
        dialog.setWindowTitle("➕ Kirim qo'shish")
        dialog.setFixedSize(380, 260)
        dialog.setStyleSheet(DARK_STYLE)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 25, 25, 25)
        
        info_label = QLabel("💰 Savdo bo'lmagan naqd kirim\n(masalan: eski qarz qaytarildi)")
        info_label.setStyleSheet("color: #a0a0b8; font-size: 13px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        amount_label = QLabel("Summa:")
        amount_label.setStyleSheet("color: #a0a0b8; font-size: 13px;")
        layout.addWidget(amount_label)
        
        amount_input = QDoubleSpinBox()
        amount_input.setRange(0, 1000000000)
        amount_input.setSuffix(" so'm")
        amount_input.setMinimumHeight(40)
        amount_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #14142a; border: 2px solid #2a2a4a; border-radius: 8px;
                padding: 8px 12px; color: #e0e0e0; font-size: 16px; font-weight: bold;
            }
            QDoubleSpinBox:focus { border: 2px solid #6c63ff; }
        """)
        layout.addWidget(amount_input)
        
        note_label = QLabel("Izoh (ixtiyoriy):")
        note_label.setStyleSheet("color: #a0a0b8; font-size: 13px;")
        layout.addWidget(note_label)
        
        note_input = QLineEdit()
        note_input.setPlaceholderText("masalan: Aziz akaning qarzi")
        note_input.setMinimumHeight(35)
        note_input.setStyleSheet("""
            QLineEdit {
                background: #14142a; border: 2px solid #2a2a4a; border-radius: 8px;
                padding: 6px 10px; color: #e0e0e0; font-size: 13px;
            }
            QLineEdit:focus { border: 2px solid #6c63ff; }
        """)
        layout.addWidget(note_input)
        
        layout.addSpacing(10)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        save_btn = QPushButton("✅ Qo'shish")
        save_btn.setObjectName("successButton")
        save_btn.setFixedHeight(42)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Bekor qilish")
        cancel_btn.setObjectName("dangerButton")
        cancel_btn.setFixedHeight(42)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        def save():
            amount = amount_input.value()
            if amount <= 0:
                QMessageBox.warning(dialog, "Xatolik", "Iltimos, summani kiriting!")
                return
            note = note_input.text().strip()
            user_id = self.user.id if self.user else None
            result = self.income_repo.create_income(amount, note, user_id)
            if result:
                dialog.accept()
                self.load_data()
                QMessageBox.information(self, "Muvaffaqiyat", f"✅ {amount:,.0f} so'm kirim qo'shildi!")
            else:
                QMessageBox.warning(dialog, "Xatolik", "Kirimni saqlashda xatolik yuz berdi!")
        
        save_btn.clicked.connect(save)
        dialog.exec()
    
    def create_stat_card(self, icon, title, value, color):
        card = QWidget()
        card.setObjectName(color)
        card.setFixedHeight(100)
        card.setStyleSheet("""
            QWidget {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 10px;
            }
            QWidget#cardBlue:hover { border-color: #6c63ff; }
            QWidget#cardRed:hover { border-color: #ff6b6b; }
            QWidget#cardGreen:hover { border-color: #00c853; }
            QWidget#cardOrange:hover { border-color: #ffa726; }
            QWidget#cardPurple:hover { border-color: #ab47bc; }
            QWidget#cardTeal:hover { border-color: #26c6da; }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(2)
        layout.setContentsMargins(15, 10, 15, 10)
        
        top_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 22px; background: transparent;")
        top_layout.addWidget(icon_label)
        top_layout.addStretch()
        
        value_label = QLabel(value)
        value_label.setObjectName("cardValue")
        value_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white; background: transparent;")
        top_layout.addWidget(value_label)
        
        layout.addLayout(top_layout)
        
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setStyleSheet("color: #a0a0b8; font-size: 12px; background: transparent;")
        layout.addWidget(title_label)
        
        return card
    
    def update_date_label(self):
        self.date_label.setText(self.current_date.toString("dd.MM.yyyy"))
    
    def prev_day(self):
        self.current_date = self.current_date.addDays(-1)
        self.update_date_label()
        self.load_data()
    
    def next_day(self):
        today = QDate.currentDate()
        if self.current_date < today:
            self.current_date = self.current_date.addDays(1)
            self.update_date_label()
            self.load_data()
    
    def go_today(self):
        self.current_date = QDate.currentDate()
        self.update_date_label()
        self.load_data()
    
    def load_data(self):
        try:
            self.update_date_label()
            
            selected_date = self.current_date.toString("yyyy-MM-dd")
            
            products = self.product_controller.get_all_products()
            total_products = len(products)
            total_cost = sum(p['cost_price'] * p['quantity'] for p in products)
            total_value = sum(p['sell_price'] * p['quantity'] for p in products)
            
            sales_data = self.sale_repo.get_sales_with_items(selected_date, selected_date)
            
            today_sales = 0
            today_profit = 0
            cash_sales = 0
            card_sales = 0
            debt_sales = 0
            bonus_total = 0
            
            for sale in sales_data:
                # Chegirma va bonus alohida ustunlarda saqlanadi (models.py: Sale dataclass)
                # discount / discount_amount - chegirma, bonus_amount - bonus
                discount = sale.discount_amount or sale.discount or 0
                bonus = sale.bonus_amount or 0
                bonus_total += discount + bonus
                
                if sale.payment_type == 'Naxt':
                    cash_sales += sale.total_amount
                    today_sales += sale.total_amount
                    today_profit += sale.total_profit
                elif sale.payment_type == 'Plastik':
                    card_sales += sale.total_amount
                    today_sales += sale.total_amount
                    today_profit += sale.total_profit
                elif sale.payment_type == 'Naxt+Plastik':
                    # Aralash to'lov: bir qismi naqd, bir qismi plastik kartadan
                    cash_part = getattr(sale, 'cash_amount', 0) or 0
                    card_part = getattr(sale, 'card_amount', 0) or 0
                    cash_sales += cash_part
                    card_sales += card_part
                    today_sales += sale.total_amount
                    today_profit += sale.total_profit
                elif sale.payment_type == 'Nasiya':
                    debt_sales += sale.total_amount
                else:
                    # Kutilmagan/notanish to'lov turi (masalan bo'sh yoki eski format) -
                    # pul "yo'qolib" ketmasligi uchun ehtiyot chorasi sifatida naqd deb hisoblaymiz
                    print(f"⚠️ Notanish to'lov turi: '{sale.payment_type}' (sale id={sale.id}) - Naxt deb hisoblandi")
                    cash_sales += sale.total_amount
                    today_sales += sale.total_amount
                    today_profit += sale.total_profit
            
            expenses = self.expense_repo.get_all(selected_date, selected_date)
            total_expense = sum(e['amount'] for e in expenses) if expenses else 0
            
            # Xarajat qaysi kassadan yechilgani (Naxt/Plastik) bo'yicha ajratamiz.
            # "payment_type" ustuni bo'lmagan eski yozuvlar Naxt deb hisoblanadi.
            cash_expense_total = 0
            card_expense_total = 0
            if expenses:
                for e in expenses:
                    e_payment_type = e['payment_type'] if 'payment_type' in e.keys() and e['payment_type'] else 'Naxt'
                    if e_payment_type == 'Plastik':
                        card_expense_total += e['amount']
                    else:
                        cash_expense_total += e['amount']
            
            # Savdo bilan bog'liq bo'lmagan naqd kirim (masalan eski qarz qaytarilishi) -
            # FOYDA hisoblanmaydi, faqat kassadagi qoldiqqa qo'shiladi
            today_incomes = self.income_repo.get_by_date(selected_date)
            today_income_total = sum(i['amount'] for i in today_incomes) if today_incomes else 0
            
            net_profit = today_profit - total_expense - bonus_total
            # MUHIM: "Bugungi qoldiq" - kassadagi jismoniy naqd pul qoldig'i.
            # Plastik (karta) orqali kelgan pul bankka tushadi, kassada yo'q,
            # shuning uchun faqat naqd (cash_sales) qismidan hisoblanadi.
            # Qo'lda kiritilgan kirim (today_income_total) ham naqd pul bo'lgani
            # uchun qoldiqqa qo'shiladi, lekin foyda hisobiga kirmaydi.
            # Xarajat ham qaysi kassadan yechilgan bo'lsa, shu qoldiqdan kamayadi:
            # Naxt xarajat -> naqd qoldiqdan, Plastik xarajat -> karta qoldig'idan.
            today_balance = cash_sales + today_income_total - cash_expense_total - bonus_total
            
            # Plastik (karta) qoldig'i: kartaga tushgan savdo puli minus
            # kartadan yechilgan (Plastik deb belgilangan) xarajatlar.
            card_balance = card_sales - card_expense_total
            
            all_sales = self.sale_repo.get_sales_with_items()
            # MUHIM: Nasiya (hali to'lanmagan qarz) sotuvlarning foydasi "Jami foyda"ga
            # kirmaydi, chunki pul hali kelmagan. Qarz to'langandan keyin (debt_paid=1)
            # yoki to'lov turi Nasiya bo'lmasa - o'sha payt foyda hisobga kiradi.
            total_profit = sum(
                s.total_profit for s in all_sales
                if not (s.payment_type == 'Nasiya' and not s.debt_paid)
            ) if all_sales else 0
            
            stats = {
                'products_count': total_products,
                'total_cost': total_cost,
                'total_value': total_value,
                'today_sales': today_sales,
                'today_profit': today_profit,
                'total_profit': total_profit,
                'total_expense': total_expense,
                'bonus_total': bonus_total,
                'net_profit': net_profit,
                'cash_sales': cash_sales,
                'card_sales': card_sales,
                'debt_sales': debt_sales,
                'today_balance': today_balance,
                'card_balance': card_balance
            }
            
            for key, card in self.cards.items():
                value_label = card.findChild(QLabel, "cardValue")
                if not value_label:
                    continue
                
                if key == 'products_count':
                    value_label.setText(str(stats.get(key, 0)))
                else:
                    val = stats.get(key, 0)
                    if val < 0:
                        value_label.setText(f"-{abs(val):,.0f} so'm")
                        value_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #ff6b6b; background: transparent;")
                    else:
                        value_label.setText(f"{val:,.0f} so'm")
                        value_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white; background: transparent;")
            
            self.load_top_products(selected_date)
            
        except Exception as e:
            print(f"❌ Dashboard ma'lumotlarini yuklashda xatolik: {e}")
            import traceback
            traceback.print_exc()
    
    def load_top_products(self, selected_date):
        try:
            sales_data = self.sale_repo.get_sales_with_items(selected_date, selected_date)
            
            product_stats = {}
            for sale in sales_data:
                if hasattr(sale, 'items') and sale.items:
                    for item in sale.items:
                        product_name = item.product_name if hasattr(item, 'product_name') else f"ID:{item.product_id}"
                        if product_name not in product_stats:
                            product_stats[product_name] = {
                                'quantity': 0,
                                'total': 0
                            }
                        product_stats[product_name]['quantity'] += item.quantity
                        product_stats[product_name]['total'] += item.subtotal
            
            sorted_products = sorted(
                product_stats.items(),
                key=lambda x: x[1]['quantity'],
                reverse=True
            )[:10]
            
            self.top_products_table.setRowCount(len(sorted_products))
            
            for i, (name, data) in enumerate(sorted_products):
                self.top_products_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                self.top_products_table.setItem(i, 1, QTableWidgetItem(name))
                self.top_products_table.setItem(i, 2, QTableWidgetItem(f"{data['quantity']:,.2f}"))
                self.top_products_table.setItem(i, 3, QTableWidgetItem(f"{data['total']:,.0f} so'm"))
            
            self.top_products_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"❌ Top products yuklashda xatolik: {e}")