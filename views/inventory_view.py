# views/inventory_view.py - TO'LIQ VA YAXSHILANGAN

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils.styles import DARK_STYLE
from controllers.product_controller import ProductController
from controllers.firm_controller import FirmController
from models.repositories import PurchaseRepository, SaleRepository, ProductRepository, FirmDebtRepository
from datetime import datetime, timedelta
import os


class InventoryView(QWidget):
    def __init__(self):
        super().__init__()
        self.product_controller = ProductController()
        self.firm_controller = FirmController()
        self.purchase_repo = PurchaseRepository()
        self.sale_repo = SaleRepository()
        self.product_repo = ProductRepository()
        self.debt_repo = FirmDebtRepository()
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.load_inventory_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ===== HEADER =====
        header_layout = QHBoxLayout()
        
        title = QLabel("📦 Ombor boshqaruvi")
        title.setObjectName("titleLabel")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Yangilash")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.setMinimumWidth(150)
        refresh_btn.clicked.connect(self.load_inventory_data)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # ===== STATISTIKA =====
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.total_products_label = self._create_stat_card("📦 Jami mahsulotlar", "0")
        stats_layout.addWidget(self.total_products_label)
        
        self.total_stock_label = self._create_stat_card("📊 Jami ombor", "0 dona")
        stats_layout.addWidget(self.total_stock_label)
        
        self.low_stock_label = self._create_stat_card("⚠️ Kam qolganlar", "0 ta", "#ff6b35")
        stats_layout.addWidget(self.low_stock_label)
        
        self.total_debt_label = self._create_stat_card("💰 Nasiya qarzlari", "0 so'm", "#ff6b35")
        stats_layout.addWidget(self.total_debt_label)
        
        self.total_firm_debt_label = self._create_stat_card("🏢 Firmalar qarzi", "0 so'm", "#f59e0b")
        stats_layout.addWidget(self.total_firm_debt_label)
        
        layout.addLayout(stats_layout)
        
        # ===== TAB WIDGET =====
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 10px;
            }
            QTabBar::tab {
                background: #1a1a2e;
                color: #a0a0b8;
                padding: 10px 20px;
                border: none;
                border-bottom: 2px solid transparent;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                color: #6c63ff;
                border-bottom: 2px solid #6c63ff;
            }
            QTabBar::tab:hover {
                color: #ffffff;
            }
        """)
        
        # ===== TAB 1: OMBOR HOLATI =====
        stock_tab = QWidget()
        stock_layout = QVBoxLayout(stock_tab)
        stock_layout.setContentsMargins(10, 10, 10, 10)
        
        search_layout = QHBoxLayout()
        self.stock_search = QLineEdit()
        self.stock_search.setPlaceholderText("🔍 Mahsulot qidirish...")
        self.stock_search.setMinimumHeight(40)
        self.stock_search.setMinimumWidth(300)
        self.stock_search.setStyleSheet("""
            QLineEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 15px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        self.stock_search.textChanged.connect(self.filter_stock)
        search_layout.addWidget(self.stock_search)
        search_layout.addStretch()
        stock_layout.addLayout(search_layout)
        
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(8)
        self.stock_table.setHorizontalHeaderLabels([
            'ID', 'Mahsulot nomi', 'Kategoriya', 'Tannarx (so\'m)', 
            'Sotuv narxi (so\'m)', 'Miqdor', 'Jami qiymat', 'Holat'
        ])
        self.stock_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.stock_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.stock_table.horizontalHeader().setStretchLastSection(True)
        self.stock_table.setStyleSheet("""
            QTableWidget {
                background: #1a1a2e;
                border: none;
                border-radius: 10px;
                gridline-color: #2a2a4a;
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
        self.stock_table.verticalHeader().setDefaultSectionSize(50)
        stock_layout.addWidget(self.stock_table)
        
        self.tab_widget.addTab(stock_tab, "📦 Ombor holati")
        
        # ===== TAB 2: XARIDLAR TARIXI =====
        purchase_tab = QWidget()
        purchase_layout = QVBoxLayout(purchase_tab)
        purchase_layout.setContentsMargins(10, 10, 10, 10)
        
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        date_label1 = QLabel("📅 Sana:")
        date_label1.setStyleSheet("color: #a0a0b8; font-size: 13px;")
        filter_layout.addWidget(date_label1)
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd.MM.yyyy")
        self.start_date.setMinimumWidth(120)
        self.start_date.setMinimumHeight(35)
        self.start_date.setStyleSheet("""
            QDateEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 5px 10px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QDateEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        filter_layout.addWidget(self.start_date)
        
        date_label2 = QLabel(" - ")
        date_label2.setStyleSheet("color: #a0a0b8; font-size: 14px;")
        filter_layout.addWidget(date_label2)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd.MM.yyyy")
        self.end_date.setMinimumWidth(120)
        self.end_date.setMinimumHeight(35)
        self.end_date.setStyleSheet("""
            QDateEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 5px 10px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QDateEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        filter_layout.addWidget(self.end_date)
        
        filter_btn = QPushButton("🔍 Filtr")
        filter_btn.setObjectName("primaryButton")
        filter_btn.setMinimumHeight(35)
        filter_btn.setMinimumWidth(100)
        filter_btn.clicked.connect(self.load_purchase_history)
        filter_layout.addWidget(filter_btn)
        
        filter_layout.addStretch()
        purchase_layout.addLayout(filter_layout)
        
        self.purchase_table = QTableWidget()
        self.purchase_table.setColumnCount(9)
        self.purchase_table.setHorizontalHeaderLabels([
            'ID', 'Mahsulot', 'Miqdor', 'Tannarx (so\'m)', 
            'Tannarx ($)', 'Jami summa', "To'lov turi", 'Sana', "To'lov muddati"
        ])
        self.purchase_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.purchase_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.purchase_table.horizontalHeader().setStretchLastSection(True)
        self.purchase_table.setStyleSheet("""
            QTableWidget {
                background: #1a1a2e;
                border: none;
                border-radius: 10px;
                gridline-color: #2a2a4a;
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
        self.purchase_table.verticalHeader().setDefaultSectionSize(50)
        purchase_layout.addWidget(self.purchase_table)
        
        purchase_btn_layout = QHBoxLayout()
        purchase_btn_layout.setSpacing(10)
        purchase_btn_layout.addStretch()
        
        edit_purchase_btn = QPushButton("✏️ Tahrirlash")
        edit_purchase_btn.setObjectName("primaryButton")
        edit_purchase_btn.setMinimumHeight(40)
        edit_purchase_btn.setMinimumWidth(130)
        edit_purchase_btn.clicked.connect(self.edit_purchase)
        purchase_btn_layout.addWidget(edit_purchase_btn)
        
        delete_purchase_btn = QPushButton("🗑️ O'chirish")
        delete_purchase_btn.setObjectName("dangerButton")
        delete_purchase_btn.setMinimumHeight(40)
        delete_purchase_btn.setMinimumWidth(130)
        delete_purchase_btn.clicked.connect(self.delete_purchase)
        purchase_btn_layout.addWidget(delete_purchase_btn)
        
        purchase_layout.addLayout(purchase_btn_layout)
        
        self.tab_widget.addTab(purchase_tab, "📋 Xaridlar tarixi")
        
        # ===== TAB 3: NASIYA QARZLARI =====
        debt_tab = QWidget()
        debt_layout = QVBoxLayout(debt_tab)
        debt_layout.setContentsMargins(10, 10, 10, 10)
        
        self.debt_table = QTableWidget()
        self.debt_table.setColumnCount(9)
        self.debt_table.setHorizontalHeaderLabels([
            'ID', 'Mahsulot', 'Miqdor', 'Tannarx (so\'m)', 
            'Tannarx ($)', 'Jami qarz', 'Xarid sanasi', "To'lov muddati", 'Holat'
        ])
        self.debt_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.debt_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.debt_table.horizontalHeader().setStretchLastSection(True)
        self.debt_table.setStyleSheet("""
            QTableWidget {
                background: #1a1a2e;
                border: none;
                border-radius: 10px;
                gridline-color: #2a2a4a;
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
        self.debt_table.verticalHeader().setDefaultSectionSize(50)
        debt_layout.addWidget(self.debt_table)
        
        debt_btn_layout = QHBoxLayout()
        debt_btn_layout.setSpacing(10)
        debt_btn_layout.addStretch()
        
        pay_btn = QPushButton("✅ To'landi deb belgilash")
        pay_btn.setObjectName("successButton")
        pay_btn.setMinimumHeight(40)
        pay_btn.setMinimumWidth(180)
        pay_btn.clicked.connect(self.mark_debt_as_paid)
        debt_btn_layout.addWidget(pay_btn)
        
        delete_debt_btn = QPushButton("🗑️ O'chirish")
        delete_debt_btn.setObjectName("dangerButton")
        delete_debt_btn.setMinimumHeight(40)
        delete_debt_btn.setMinimumWidth(130)
        delete_debt_btn.clicked.connect(self.delete_debt)
        debt_btn_layout.addWidget(delete_debt_btn)
        
        debt_layout.addLayout(debt_btn_layout)
        
        self.tab_widget.addTab(debt_tab, "💳 Nasiya qarzlari")
        
        # ===== TAB 4: FIRMALAR =====
        firms_tab = QWidget()
        firms_layout = QVBoxLayout(firms_tab)
        firms_layout.setContentsMargins(10, 10, 10, 10)
        
        firms_header = QHBoxLayout()
        firms_header.setSpacing(10)
        
        firms_label = QLabel("🏢 Firmalar ro'yxati")
        firms_label.setStyleSheet("color: #a0a0b8; font-size: 16px; font-weight: bold;")
        firms_header.addWidget(firms_label)
        firms_header.addStretch()
        
        add_firm_btn = QPushButton("➕ Yangi firma")
        add_firm_btn.setObjectName("primaryButton")
        add_firm_btn.setMinimumHeight(35)
        add_firm_btn.setMinimumWidth(130)
        add_firm_btn.clicked.connect(self.show_add_firm_dialog)
        firms_header.addWidget(add_firm_btn)
        
        add_debt_btn = QPushButton("💰 Qarz qo'shish")
        add_debt_btn.setObjectName("warningButton")
        add_debt_btn.setMinimumHeight(35)
        add_debt_btn.setMinimumWidth(130)
        add_debt_btn.setStyleSheet("""
            QPushButton#warningButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #f59e0b, stop: 1 #d97706);
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }
            QPushButton#warningButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #fbbf24, stop: 1 #f59e0b);
            }
        """)
        add_debt_btn.clicked.connect(self.show_add_debt_dialog)
        firms_header.addWidget(add_debt_btn)
        
        check_firms_btn = QPushButton("🔍 Tekshirish")
        check_firms_btn.setObjectName("primaryButton")
        check_firms_btn.setMinimumHeight(35)
        check_firms_btn.setMinimumWidth(120)
        check_firms_btn.clicked.connect(self.check_firms)
        firms_header.addWidget(check_firms_btn)
        
        firms_layout.addLayout(firms_header)
        
        self.firms_table = QTableWidget()
        self.firms_table.setColumnCount(6)
        self.firms_table.setHorizontalHeaderLabels([
            'ID', 'Firma nomi', 'Telefon', 'Jami qarz', 'Manzil', 'Qarzlar soni'
        ])
        self.firms_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.firms_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.firms_table.horizontalHeader().setStretchLastSection(True)
        self.firms_table.setStyleSheet("""
            QTableWidget {
                background: #1a1a2e;
                border: none;
                border-radius: 10px;
                gridline-color: #2a2a4a;
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
        self.firms_table.verticalHeader().setDefaultSectionSize(50)
        self.firms_table.itemDoubleClicked.connect(self.view_firm_details)
        firms_layout.addWidget(self.firms_table)
        
        firms_btn_layout = QHBoxLayout()
        firms_btn_layout.setSpacing(10)
        firms_btn_layout.addStretch()
        
        view_firm_btn = QPushButton("👁️ Batafsil")
        view_firm_btn.setObjectName("primaryButton")
        view_firm_btn.setMinimumHeight(35)
        view_firm_btn.setMinimumWidth(110)
        view_firm_btn.clicked.connect(self.view_firm_details_selected)
        firms_btn_layout.addWidget(view_firm_btn)
        
        edit_firm_btn = QPushButton("✏️ Tahrirlash")
        edit_firm_btn.setObjectName("primaryButton")
        edit_firm_btn.setMinimumHeight(35)
        edit_firm_btn.setMinimumWidth(110)
        edit_firm_btn.clicked.connect(self.edit_firm)
        firms_btn_layout.addWidget(edit_firm_btn)
        
        delete_firm_btn = QPushButton("🗑️ O'chirish")
        delete_firm_btn.setObjectName("dangerButton")
        delete_firm_btn.setMinimumHeight(35)
        delete_firm_btn.setMinimumWidth(110)
        delete_firm_btn.clicked.connect(self.delete_firm)
        firms_btn_layout.addWidget(delete_firm_btn)
        
        firms_layout.addLayout(firms_btn_layout)
        
        self.tab_widget.addTab(firms_tab, "🏢 Firmalar")
        
        layout.addWidget(self.tab_widget)
    
    # ============================================================
    # STATISTIK KARTA
    # ============================================================
    def _create_stat_card(self, title, value, color="#6c63ff"):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 10px;
                padding: 15px;
                min-width: 160px;
                min-height: 80px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #a0a0b8; font-size: 13px; font-weight: 500;")
        card_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            color: {color};
            font-size: 22px;
            font-weight: bold;
        """)
        value_label.setObjectName("statValue")
        card_layout.addWidget(value_label)
        
        return card
    
    # ============================================================
    # MA'LUMOTLARNI YUKLASH
    # ============================================================
    def load_inventory_data(self):
        try:
            products = self.product_controller.get_all_products()
            
            total_products = len(products)
            total_stock = sum(p['quantity'] for p in products)
            low_stock = sum(1 for p in products if p['quantity'] <= p.get('min_quantity', 5))
            total_debt = self.purchase_repo.get_total_debt()
            total_firm_debt = self.firm_controller.get_total_debt()
            
            # Statistik kartalarni yangilash
            for card in [self.total_products_label, self.total_stock_label, 
                        self.low_stock_label, self.total_debt_label, 
                        self.total_firm_debt_label]:
                value_label = card.findChild(QLabel, "statValue")
                if value_label:
                    if card == self.total_products_label:
                        value_label.setText(str(total_products))
                    elif card == self.total_stock_label:
                        value_label.setText(f"{total_stock:,.0f} dona")
                    elif card == self.low_stock_label:
                        value_label.setText(f"{low_stock} ta")
                    elif card == self.total_debt_label:
                        value_label.setText(f"{total_debt:,.0f} so'm")
                    elif card == self.total_firm_debt_label:
                        value_label.setText(f"{total_firm_debt:,.0f} so'm")
            
            self.load_stock_table(products)
            self.load_purchase_history()
            self.load_debts()
            self.load_firms()
            
            self.update_main_window_dots()
            
            print(f"✅ Ombor ma'lumotlari yuklandi: {total_products} ta mahsulot")
            
        except Exception as e:
            print(f"❌ Ombor ma'lumotlarini yuklashda xatolik: {e}")
            import traceback
            traceback.print_exc()
    
    # ============================================================
    # OMBOR HOLATI
    # ============================================================
    def load_stock_table(self, products):
        try:
            self.stock_table.setRowCount(len(products))
            for i, product in enumerate(products):
                self.stock_table.setItem(i, 0, QTableWidgetItem(str(product['id'])))
                self.stock_table.setItem(i, 1, QTableWidgetItem(product['name']))
                self.stock_table.setItem(i, 2, QTableWidgetItem(product.get('category', '')))
                self.stock_table.setItem(i, 3, QTableWidgetItem(f"{product['cost_price']:,.2f}"))
                self.stock_table.setItem(i, 4, QTableWidgetItem(f"{product['sell_price']:,.2f}"))
                self.stock_table.setItem(i, 5, QTableWidgetItem(f"{product['quantity']} {product.get('unit', 'dona')}"))
                
                total_value = product['cost_price'] * product['quantity']
                self.stock_table.setItem(i, 6, QTableWidgetItem(f"{total_value:,.2f}"))
                
                if product['quantity'] <= product.get('min_quantity', 5):
                    status = "⚠️ Kam qolgan"
                    status_item = QTableWidgetItem(status)
                    status_item.setBackground(Qt.GlobalColor.darkRed)
                    status_item.setForeground(Qt.GlobalColor.white)
                else:
                    status = "✅ Yaxshi"
                    status_item = QTableWidgetItem(status)
                
                self.stock_table.setItem(i, 7, status_item)
            
            self.stock_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"❌ Ombor jadvalini yuklashda xatolik: {e}")
    
    def filter_stock(self):
        search_text = self.stock_search.text().lower()
        for row in range(self.stock_table.rowCount()):
            name_item = self.stock_table.item(row, 1)
            if name_item:
                show = search_text in name_item.text().lower()
                self.stock_table.setRowHidden(row, not show)
    
    # ============================================================
    # XARIDLAR TARIXI
    # ============================================================
    def load_purchase_history(self):
        try:
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")
            
            purchases = self.purchase_repo.get_purchases_by_date(start_date, end_date)
            
            self.purchase_table.setRowCount(len(purchases))
            for i, purchase in enumerate(purchases):
                self.purchase_table.setItem(i, 0, QTableWidgetItem(str(purchase['id'])))
                self.purchase_table.setItem(i, 1, QTableWidgetItem(purchase.get('product_name', '')))
                self.purchase_table.setItem(i, 2, QTableWidgetItem(f"{purchase['quantity']}"))
                self.purchase_table.setItem(i, 3, QTableWidgetItem(f"{purchase['unit_cost']:,.2f}"))
                
                dollar_cost = purchase.get('dollar_cost', 0)
                if dollar_cost > 0:
                    self.purchase_table.setItem(i, 4, QTableWidgetItem(f"{dollar_cost:,.2f}$"))
                else:
                    self.purchase_table.setItem(i, 4, QTableWidgetItem("-"))
                
                self.purchase_table.setItem(i, 5, QTableWidgetItem(f"{purchase['total_cost']:,.2f}"))
                
                payment_type = purchase.get('payment_type', 'Naxt')
                if payment_type == 'Nasiya':
                    payment_type = "📝 Nasiya"
                else:
                    payment_type = "💵 Naxt"
                self.purchase_table.setItem(i, 6, QTableWidgetItem(payment_type))
                
                self.purchase_table.setItem(i, 7, QTableWidgetItem(purchase.get('purchase_date', '')))
                
                due_date = purchase.get('due_date', '')
                if due_date:
                    try:
                        due = datetime.strptime(due_date, '%Y-%m-%d').date()
                        today = datetime.now().date()
                        days_left = (due - today).days
                        
                        if days_left < 0:
                            due_date = f"❌ {due_date} (o'tgan)"
                        elif days_left <= 7:
                            due_date = f"⚠️ {due_date} ({days_left} kun)"
                    except:
                        pass
                
                self.purchase_table.setItem(i, 8, QTableWidgetItem(due_date or '-'))
            
            self.purchase_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"❌ Xaridlar tarixini yuklashda xatolik: {e}")
    
    def edit_purchase(self):
        try:
            current_row = self.purchase_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Ogohlantirish", "Iltimos, tahrirlamoqchi bo'lgan xaridni tanlang!")
                return
            
            purchase_id_item = self.purchase_table.item(current_row, 0)
            if not purchase_id_item:
                return
            purchase_id = int(purchase_id_item.text())
            
            purchase = self.purchase_repo.get_purchase_by_id(purchase_id)
            if not purchase:
                QMessageBox.warning(self, "Xatolik", "Xarid ma'lumotlari topilmadi!")
                return
            
            product_id = purchase.get('product_id')
            product_name = purchase.get('product_name', '')
            old_quantity = float(purchase.get('quantity', 0))
            old_unit_cost = float(purchase.get('unit_cost', 0))
            
            dialog = QDialog(self)
            dialog.setWindowTitle("✏️ Xaridni tahrirlash")
            dialog.setFixedSize(450, 400)
            dialog.setStyleSheet(DARK_STYLE)
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(12)
            layout.setContentsMargins(25, 25, 25, 25)
            
            info_label = QLabel(f"📦 Mahsulot: {product_name}")
            info_label.setStyleSheet("color: #e0e0e0; font-size: 15px; font-weight: bold;")
            layout.addWidget(info_label)
            
            layout.addSpacing(5)
            
            qty_label = QLabel("📏 Miqdor:")
            qty_label.setStyleSheet("color: #a0a0b8; font-size: 13px;")
            layout.addWidget(qty_label)
            
            quantity_input = QDoubleSpinBox()
            quantity_input.setRange(0.01, 1000000)
            quantity_input.setDecimals(2)
            quantity_input.setValue(old_quantity)
            quantity_input.setMinimumHeight(35)
            quantity_input.setMinimumWidth(300)
            quantity_input.setStyleSheet("""
                QDoubleSpinBox {
                    background: #14142a; border: 2px solid #2a2a4a; border-radius: 8px;
                    padding: 6px 10px; color: #e0e0e0; font-size: 14px; font-weight: bold;
                }
                QDoubleSpinBox:focus { border: 2px solid #6c63ff; }
            """)
            layout.addWidget(quantity_input)
            
            cost_label = QLabel("💰 Tannarx (birlik uchun):")
            cost_label.setStyleSheet("color: #a0a0b8; font-size: 13px;")
            layout.addWidget(cost_label)
            
            cost_input = QDoubleSpinBox()
            cost_input.setRange(0, 1000000000)
            cost_input.setDecimals(2)
            cost_input.setValue(old_unit_cost)
            cost_input.setMinimumHeight(35)
            cost_input.setMinimumWidth(300)
            cost_input.setStyleSheet("""
                QDoubleSpinBox {
                    background: #14142a; border: 2px solid #2a2a4a; border-radius: 8px;
                    padding: 6px 10px; color: #e0e0e0; font-size: 14px; font-weight: bold;
                }
                QDoubleSpinBox:focus { border: 2px solid #6c63ff; }
            """)
            layout.addWidget(cost_input)
            
            layout.addSpacing(5)
            
            total_label = QLabel("💵 Jami summa:")
            total_label.setStyleSheet("color: #a0a0b8; font-size: 13px;")
            layout.addWidget(total_label)
            
            total_value = QLabel(f"{old_quantity * old_unit_cost:,.0f} so'm")
            total_value.setStyleSheet("color: #00c853; font-size: 18px; font-weight: bold;")
            layout.addWidget(total_value)
            
            def update_total():
                total_value.setText(f"{quantity_input.value() * cost_input.value():,.0f} so'm")
            
            quantity_input.valueChanged.connect(update_total)
            cost_input.valueChanged.connect(update_total)
            
            layout.addSpacing(10)
            
            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(15)
            
            save_btn = QPushButton("💾 Saqlash")
            save_btn.setObjectName("successButton")
            save_btn.setFixedHeight(42)
            save_btn.setMinimumWidth(120)
            btn_layout.addWidget(save_btn)
            
            cancel_btn = QPushButton("❌ Bekor qilish")
            cancel_btn.setObjectName("dangerButton")
            cancel_btn.setFixedHeight(42)
            cancel_btn.setMinimumWidth(120)
            cancel_btn.clicked.connect(dialog.reject)
            btn_layout.addWidget(cancel_btn)
            
            layout.addLayout(btn_layout)
            
            def save_changes():
                new_quantity = quantity_input.value()
                new_unit_cost = cost_input.value()
                new_total_cost = new_quantity * new_unit_cost
                quantity_delta = new_quantity - old_quantity
                
                msg = f"'{product_name}' xaridi tahrirlanadi:\n\n"
                msg += f"📏 Miqdor: {old_quantity:g} → {new_quantity:g}\n"
                msg += f"💰 Tannarx: {old_unit_cost:,.0f} → {new_unit_cost:,.0f} so'm\n"
                msg += f"💵 Jami: {new_total_cost:,.0f} so'm\n"
                if quantity_delta != 0:
                    sign = "+" if quantity_delta > 0 else ""
                    msg += f"\n📦 Omordagi '{product_name}' qoldig'i {sign}{quantity_delta:g} ga o'zgaradi!"
                
                reply = QMessageBox.question(
                    dialog, "Tasdiqlash", msg,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
                
                result = self.purchase_repo.update_purchase(purchase_id, {
                    'quantity': new_quantity,
                    'unit_cost': new_unit_cost,
                    'total_cost': new_total_cost
                })
                
                if not result:
                    QMessageBox.warning(dialog, "Xatolik", "Xaridni yangilashda xatolik yuz berdi!")
                    return
                
                if quantity_delta != 0 and product_id:
                    self.product_repo.update_stock(product_id, quantity_delta)
                
                QMessageBox.information(dialog, "Muvaffaqiyat", "✅ Xarid muvaffaqiyatli tahrirlandi!")
                dialog.accept()
                self.load_purchase_history()
                self.load_inventory_data()
            
            save_btn.clicked.connect(save_changes)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Xaridni tahrirlashda xatolik: {str(e)}")
            print(f"❌ Edit purchase error: {e}")
    
    def delete_purchase(self):
        try:
            current_row = self.purchase_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Ogohlantirish", "Iltimos, o'chirmoqchi bo'lgan xaridni tanlang!")
                return
            
            purchase_id_item = self.purchase_table.item(current_row, 0)
            if not purchase_id_item:
                return
            purchase_id = int(purchase_id_item.text())
            
            purchase = self.purchase_repo.get_purchase_by_id(purchase_id)
            if not purchase:
                QMessageBox.warning(self, "Xatolik", "Xarid ma'lumotlari topilmadi!")
                return
            
            product_name = purchase.get('product_name', '')
            quantity = float(purchase.get('quantity', 0))
            
            reply = QMessageBox.question(
                self, "Tasdiqlash",
                f"'{product_name}' xaridini ({quantity:g} dona) butunlay o'chirmoqchimisiz?\n\n"
                f"⚠️ Ombordagi qoldiq shu miqdorga kamaytiriladi.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            result = self.purchase_repo.delete_purchase(purchase_id)
            if result:
                product_id = purchase.get('product_id')
                if product_id and quantity:
                    self.product_repo.update_stock(product_id, -quantity)
                QMessageBox.information(self, "Muvaffaqiyat", "✅ Xarid yozuvi o'chirildi!")
                self.load_inventory_data()
            else:
                QMessageBox.warning(self, "Xatolik", "Xaridni o'chirishda xatolik yuz berdi!")
                
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Xaridni o'chirishda xatolik: {str(e)}")
            print(f"❌ Delete purchase error: {e}")
    
    # ============================================================
    # NASIYA QARZLARI
    # ============================================================
    def load_debts(self):
        try:
            all_purchases = self.purchase_repo.get_all_purchases()
            debts = [p for p in all_purchases if p.get('payment_type') == 'Nasiya' and p.get('is_paid', 0) == 0]
            
            self.debt_table.setRowCount(len(debts))
            for i, debt in enumerate(debts):
                self.debt_table.setItem(i, 0, QTableWidgetItem(str(debt['id'])))
                self.debt_table.setItem(i, 1, QTableWidgetItem(debt.get('product_name', '')))
                self.debt_table.setItem(i, 2, QTableWidgetItem(f"{debt['quantity']}"))
                self.debt_table.setItem(i, 3, QTableWidgetItem(f"{debt['unit_cost']:,.2f}"))
                
                dollar_cost = debt.get('dollar_cost', 0)
                if dollar_cost > 0:
                    self.debt_table.setItem(i, 4, QTableWidgetItem(f"{dollar_cost:,.2f}$"))
                else:
                    self.debt_table.setItem(i, 4, QTableWidgetItem("-"))
                
                self.debt_table.setItem(i, 5, QTableWidgetItem(f"{debt['total_cost']:,.2f}"))
                self.debt_table.setItem(i, 6, QTableWidgetItem(debt.get('purchase_date', '')))
                
                due_date = debt.get('due_date', '')
                status = "✅ To'lov kutilmoqda"
                
                if due_date:
                    try:
                        due = datetime.strptime(due_date, '%Y-%m-%d').date()
                        today = datetime.now().date()
                        days_left = (due - today).days
                        
                        if days_left < 0:
                            status = "🔴 Muddati o'tgan!"
                            due_date = f"❌ {due_date}"
                            status_item = QTableWidgetItem(status)
                            status_item.setBackground(Qt.GlobalColor.darkRed)
                            status_item.setForeground(Qt.GlobalColor.white)
                        elif days_left <= 7:
                            status = f"⚠️ {days_left} kun qoldi!"
                            due_date = f"⚠️ {due_date}"
                            status_item = QTableWidgetItem(status)
                            status_item.setBackground(Qt.GlobalColor.darkYellow)
                        else:
                            status_item = QTableWidgetItem(status)
                    except:
                        status_item = QTableWidgetItem(status)
                else:
                    status_item = QTableWidgetItem(status)
                
                self.debt_table.setItem(i, 7, QTableWidgetItem(due_date or '-'))
                self.debt_table.setItem(i, 8, status_item)
            
            self.debt_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"❌ Qarzlarni yuklashda xatolik: {e}")
    
    def delete_debt(self):
        try:
            current_row = self.debt_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Ogohlantirish", "Iltimos, o'chirmoqchi bo'lgan qarzni tanlang!")
                return
            
            debt_id_item = self.debt_table.item(current_row, 0)
            if not debt_id_item:
                return
            debt_id = int(debt_id_item.text())
            
            purchase = self.purchase_repo.get_purchase_by_id(debt_id)
            if not purchase:
                QMessageBox.warning(self, "Xatolik", "Qarz ma'lumotlari topilmadi!")
                return
            
            product_name = purchase.get('product_name', '')
            quantity = float(purchase.get('quantity', 0))
            
            reply = QMessageBox.question(
                self, "Tasdiqlash",
                f"'{product_name}' bo'yicha qarz yozuvini ({quantity:g} dona) butunlay o'chirmoqchimisiz?\n\n"
                f"⚠️ Ombordagi qoldiq shu miqdorga kamaytiriladi, qarz ham bekor bo'ladi.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            result = self.purchase_repo.delete_purchase(debt_id)
            if result:
                product_id = purchase.get('product_id')
                if product_id and quantity:
                    self.product_repo.update_stock(product_id, -quantity)
                QMessageBox.information(self, "Muvaffaqiyat", "✅ Qarz yozuvi o'chirildi!")
                self.load_inventory_data()
            else:
                QMessageBox.warning(self, "Xatolik", "Qarzni o'chirishda xatolik yuz berdi!")
                
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Qarzni o'chirishda xatolik: {str(e)}")
            print(f"❌ Delete debt error: {e}")
    
    # ============================================================
    # QARZNI TO'LASH (NAXT, PLASTIK, NAXT+PLASTIK) - YAXSHILANGAN
    # ============================================================
    def mark_debt_as_paid(self):
        """Qarzni to'lash - Naxt, Plastik, Naxt+Plastik tanlash bilan + kassa tekshiruvi"""
        try:
            current_row = self.debt_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Ogohlantirish", "Iltimos, qarzni tanlang!")
                return

            debt_id = int(self.debt_table.item(current_row, 0).text())
            product_name = self.debt_table.item(current_row, 1).text()
            debt_amount_str = self.debt_table.item(current_row, 5).text()
            debt_amount = float(debt_amount_str.replace(' so\'m', '').replace(',', ''))

            dialog = QDialog(self)
            dialog.setWindowTitle("💰 Qarzni to'lash")
            dialog.setFixedSize(680, 860)
            dialog.setStyleSheet("""
                QDialog {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 #0b0e16, stop: 1 #131a2e);
                    border-radius: 16px;
                }
            """)

            main_layout = QVBoxLayout(dialog)
            main_layout.setSpacing(15)
            main_layout.setContentsMargins(35, 25, 35, 25)

            # ===== HEADER =====
            header_widget = QWidget()
            header_widget.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #1a1a3e, stop: 1 #2a1a4a);
                    border-radius: 12px;
                    padding: 15px;
                }
            """)
            header_layout = QHBoxLayout(header_widget)

            icon_label = QLabel("💰")
            icon_label.setStyleSheet("font-size: 28px; background: transparent;")
            header_layout.addWidget(icon_label)

            info_label = QLabel(
                f"📦 {product_name}\n"
                f"💳 Jami qarz: {debt_amount:,.0f} so'm"
            )
            info_label.setStyleSheet("color: #e0e0e0; font-size: 15px; font-weight: bold; background: transparent;")
            info_label.setWordWrap(True)
            header_layout.addWidget(info_label)
            header_layout.addStretch()

            main_layout.addWidget(header_widget)

            # ===== KASSA HOLATI =====
            balance_widget = QWidget()
            balance_widget.setStyleSheet("""
                QWidget {
                    background: #0f0f22;
                    border: 2px solid #2a2a4a;
                    border-radius: 10px;
                    padding: 12px;
                }
            """)
            balance_layout = QHBoxLayout(balance_widget)

            balance_title = QLabel("📅 Tanlangan kunda kassada mavjud:")
            balance_title.setStyleSheet("color: #a0a0b8; font-size: 13px; background: transparent;")
            balance_layout.addWidget(balance_title)
            balance_layout.addStretch()

            balance_value_label = QLabel("💵 0 so'm   |   💳 0 so'm")
            balance_value_label.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold; background: transparent;")
            balance_layout.addWidget(balance_value_label)

            main_layout.addWidget(balance_widget)

            # ===== TO'LOV TURI =====
            payment_label = QLabel("💳 To'lov turini tanlang:")
            payment_label.setStyleSheet("color: #a0a0b8; font-size: 14px; font-weight: 600;")
            main_layout.addWidget(payment_label)

            payment_combo = QComboBox()
            payment_combo.addItems(["💵 Naxt", "💳 Plastik", "💵💳 Naxt + Plastik"])
            payment_combo.setMinimumHeight(45)
            payment_combo.setMinimumWidth(300)
            payment_combo.setStyleSheet("""
                QComboBox {
                    background: #14142a;
                    border: 2px solid #2a2a4a;
                    border-radius: 10px;
                    padding: 8px 16px;
                    color: #e0e0e0;
                    font-size: 15px;
                    font-weight: 600;
                }
                QComboBox:focus {
                    border: 2px solid #6c63ff;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox QAbstractItemView {
                    background: #1a1a2e;
                    color: #e0e0e0;
                    selection-background-color: #4a4a8a;
                    padding: 6px;
                }
            """)
            main_layout.addWidget(payment_combo)

            # ===== NAXT + PLASTIK GROUP =====
            mixed_group = QGroupBox("💵 Naqd va 💳 Plastik bo'lib to'lash")
            mixed_group.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #6c63ff;
                    border-radius: 12px;
                    padding: 20px 20px 25px 20px;
                    margin-top: 10px;
                    background: #14142a;
                    min-height: 200px;
                }
                QGroupBox::title {
                    color: #6c63ff;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 0 12px;
                    subcontrol-origin: margin;
                    left: 10px;
                }
            """)
            mixed_layout = QVBoxLayout(mixed_group)
            mixed_layout.setSpacing(15)
            mixed_layout.setContentsMargins(10, 20, 10, 15)

            cash_widget = QWidget()
            cash_widget.setStyleSheet("background: transparent;")
            cash_layout = QHBoxLayout(cash_widget)
            cash_layout.setSpacing(12)
            cash_layout.setContentsMargins(0, 0, 0, 0)

            cash_label = QLabel("💵 Naqd pul:")
            cash_label.setStyleSheet("color: #a0a0b8; font-size: 15px; font-weight: 600; background: transparent; min-width: 110px;")
            cash_layout.addWidget(cash_label)

            cash_input = QDoubleSpinBox()
            cash_input.setRange(0, debt_amount)
            cash_input.setPrefix("so'm ")
            cash_input.setMinimumHeight(45)
            cash_input.setMinimumWidth(250)
            cash_input.setStyleSheet("""
                QDoubleSpinBox {
                    background: #1a1a2e;
                    border: 2px solid #2a2a4a;
                    border-radius: 8px;
                    padding: 8px 15px;
                    color: #00c853;
                    font-size: 16px;
                    font-weight: bold;
                }
                QDoubleSpinBox:focus {
                    border: 2px solid #6c63ff;
                }
                QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                    width: 22px;
                    background: #2a2a4a;
                    border-radius: 4px;
                }
            """)
            cash_layout.addWidget(cash_input, 1)
            cash_layout.addStretch()
            mixed_layout.addWidget(cash_widget)

            card_widget = QWidget()
            card_widget.setStyleSheet("background: transparent;")
            card_layout = QHBoxLayout(card_widget)
            card_layout.setSpacing(12)
            card_layout.setContentsMargins(0, 0, 0, 0)

            card_label = QLabel("💳 Plastik:")
            card_label.setStyleSheet("color: #a0a0b8; font-size: 15px; font-weight: 600; background: transparent; min-width: 110px;")
            card_layout.addWidget(card_label)

            card_input = QDoubleSpinBox()
            card_input.setRange(0, debt_amount)
            card_input.setPrefix("so'm ")
            card_input.setMinimumHeight(45)
            card_input.setMinimumWidth(250)
            card_input.setStyleSheet("""
                QDoubleSpinBox {
                    background: #1a1a2e;
                    border: 2px solid #2a2a4a;
                    border-radius: 8px;
                    padding: 8px 15px;
                    color: #6c63ff;
                    font-size: 16px;
                    font-weight: bold;
                }
                QDoubleSpinBox:focus {
                    border: 2px solid #6c63ff;
                }
                QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                    width: 22px;
                    background: #2a2a4a;
                    border-radius: 4px;
                }
            """)
            card_layout.addWidget(card_input, 1)
            card_layout.addStretch()
            mixed_layout.addWidget(card_widget)

            info_widget = QWidget()
            info_widget.setStyleSheet("background: transparent;")
            info_layout = QHBoxLayout(info_widget)
            info_layout.setSpacing(20)
            info_layout.setContentsMargins(0, 10, 0, 0)

            total_label = QLabel("💰 Jami:")
            total_label.setStyleSheet("color: #a0a0b8; font-size: 14px; font-weight: 600; background: transparent;")
            info_layout.addWidget(total_label)

            total_mixed_value = QLabel("0 so'm")
            total_mixed_value.setStyleSheet("color: #ffffff; font-size: 17px; font-weight: bold; background: transparent;")
            info_layout.addWidget(total_mixed_value)

            info_layout.addStretch()

            remaining_label = QLabel("📌 Qolgan:")
            remaining_label.setStyleSheet("color: #a0a0b8; font-size: 14px; font-weight: 600; background: transparent;")
            info_layout.addWidget(remaining_label)

            remaining_mixed_value = QLabel(f"{debt_amount:,.0f} so'm")
            remaining_mixed_value.setStyleSheet("color: #ff6b35; font-size: 17px; font-weight: bold; background: transparent;")
            info_layout.addWidget(remaining_mixed_value)

            mixed_layout.addWidget(info_widget)

            main_layout.addWidget(mixed_group)
            mixed_group.setVisible(False)

            # ===== SUMMARY =====
            summary_widget = QWidget()
            summary_widget.setStyleSheet("""
                QWidget {
                    background: #0f0f22;
                    border-radius: 10px;
                    padding: 15px;
                }
            """)
            summary_layout = QVBoxLayout(summary_widget)
            summary_layout.setSpacing(8)

            total_payment_widget = QWidget()
            total_payment_widget.setStyleSheet("background: transparent;")
            total_payment_layout = QHBoxLayout(total_payment_widget)
            total_payment_layout.setContentsMargins(0, 0, 0, 0)

            total_payment_label = QLabel("💰 Jami to'lov:")
            total_payment_label.setStyleSheet("color: #a0a0b8; font-size: 14px; font-weight: 600;")
            total_payment_layout.addWidget(total_payment_label)
            total_payment_layout.addStretch()

            total_payment_value = QLabel("0 so'm")
            total_payment_value.setStyleSheet("color: #ffffff; font-size: 20px; font-weight: bold;")
            total_payment_layout.addWidget(total_payment_value)

            summary_layout.addWidget(total_payment_widget)

            remaining_qarz_widget = QWidget()
            remaining_qarz_widget.setStyleSheet("background: transparent;")
            remaining_qarz_layout = QHBoxLayout(remaining_qarz_widget)
            remaining_qarz_layout.setContentsMargins(0, 0, 0, 0)

            remaining_qarz_label = QLabel("📌 Qolgan qarz:")
            remaining_qarz_label.setStyleSheet("color: #a0a0b8; font-size: 14px; font-weight: 600;")
            remaining_qarz_layout.addWidget(remaining_qarz_label)
            remaining_qarz_layout.addStretch()

            remaining_qarz_value = QLabel(f"{debt_amount:,.0f} so'm")
            remaining_qarz_value.setStyleSheet("color: #ff6b35; font-size: 20px; font-weight: bold;")
            remaining_qarz_layout.addWidget(remaining_qarz_value)

            summary_layout.addWidget(remaining_qarz_widget)

            main_layout.addWidget(summary_widget)

            # ===== SANA =====
            date_label = QLabel("📅 To'lov sanasi (qaysi kun kassasidan olinadi):")
            date_label.setStyleSheet("color: #a0a0b8; font-size: 13px;")
            main_layout.addWidget(date_label)

            date_input = QDateEdit()
            date_input.setDate(QDate.currentDate())
            date_input.setCalendarPopup(True)
            date_input.setDisplayFormat("dd.MM.yyyy")
            date_input.setMinimumHeight(40)
            date_input.setMinimumWidth(250)
            date_input.setStyleSheet("""
                QDateEdit {
                    background: #14142a;
                    border: 2px solid #2a2a4a;
                    border-radius: 8px;
                    padding: 8px 15px;
                    color: #e0e0e0;
                    font-size: 14px;
                }
                QDateEdit:focus {
                    border: 2px solid #6c63ff;
                }
                QDateEdit::drop-down {
                    border: none;
                }
            """)
            main_layout.addWidget(date_input)

            main_layout.addSpacing(10)

            # ===== TUGMALAR =====
            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(15)

            cancel_btn = QPushButton("❌ Bekor qilish")
            cancel_btn.setMinimumHeight(48)
            cancel_btn.setMinimumWidth(130)
            cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background: #1a1a32;
                    color: #a0a0b8;
                    border: 2px solid #2a2a4a;
                    border-radius: 10px;
                    padding: 8px 30px;
                    font-size: 15px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: #2a2a4a;
                    color: #d0d0e0;
                }
            """)
            cancel_btn.clicked.connect(dialog.reject)
            btn_layout.addWidget(cancel_btn)

            pay_btn = QPushButton("✅ To'lash")
            pay_btn.setMinimumHeight(48)
            pay_btn.setMinimumWidth(150)
            pay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            pay_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #00c853, stop: 1 #009624);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 8px 40px;
                    font-size: 16px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #00e863, stop: 1 #00a634);
                }
            """)
            pay_btn.clicked.connect(lambda: self._confirm_payment_with_type(
                dialog, debt_id, product_name, debt_amount,
                payment_combo, cash_input, card_input,
                total_payment_value, remaining_qarz_value, date_input
            ))
            btn_layout.addWidget(pay_btn)

            main_layout.addLayout(btn_layout)

            # ============================================================
            # FUNKSIYALAR
            # ============================================================

            def refresh_balance_label():
                """Tanlangan sana uchun mavjud naqd/plastikni yuklab, label ni yangilaydi."""
                try:
                    date_str = date_input.date().toString("yyyy-MM-dd")
                    balance = self.sale_repo.get_cash_card_balance(date_str)
                    cash_ok = balance['available_cash']
                    card_ok = balance['available_card']
                    balance_value_label.setText(
                        f"💵 {cash_ok:,.0f} so'm   |   💳 {card_ok:,.0f} so'm"
                    )
                    if cash_ok <= 0 and card_ok <= 0:
                        balance_value_label.setStyleSheet(
                            "color: #ff5252; font-size: 14px; font-weight: bold; background: transparent;"
                        )
                    else:
                        balance_value_label.setStyleSheet(
                            "color: #ffffff; font-size: 14px; font-weight: bold; background: transparent;"
                        )
                    return balance
                except Exception as e:
                    print(f"❌ Balansni yangilashda xatolik: {e}")
                    return {'available_cash': 0, 'available_card': 0}

            date_input.dateChanged.connect(refresh_balance_label)

            def on_payment_changed(text):
                is_mixed = "Naxt + Plastik" in text
                mixed_group.setVisible(is_mixed)

                if is_mixed:
                    cash_input.setValue(debt_amount)
                    card_input.setValue(0)
                    total_payment_value.setText(f"{debt_amount:,.0f} so'm")
                else:
                    cash_input.setValue(0)
                    card_input.setValue(0)
                    if "Naxt" in text:
                        cash_input.setValue(debt_amount)
                        total_payment_value.setText(f"{debt_amount:,.0f} so'm")
                    else:
                        card_input.setValue(debt_amount)
                        total_payment_value.setText(f"{debt_amount:,.0f} so'm")

                update_mixed_payment()

            payment_combo.currentTextChanged.connect(on_payment_changed)

            def update_mixed_payment():
                try:
                    cash_val = cash_input.value()
                    card_val = card_input.value()
                    total = cash_val + card_val

                    if total > debt_amount:
                        if cash_val > debt_amount:
                            cash_input.setValue(debt_amount)
                            cash_val = debt_amount
                            card_val = 0
                        else:
                            card_input.setValue(debt_amount - cash_val)
                            card_val = debt_amount - cash_val
                        total = debt_amount

                    total_mixed_value.setText(f"{total:,.0f} so'm")
                    remaining = debt_amount - total
                    if remaining < 0:
                        remaining = 0
                    remaining_mixed_value.setText(f"{remaining:,.0f} so'm")

                    if remaining <= 0:
                        remaining_mixed_value.setStyleSheet("color: #00c853; font-size: 17px; font-weight: bold; background: transparent;")
                    else:
                        remaining_mixed_value.setStyleSheet("color: #ff6b35; font-size: 17px; font-weight: bold; background: transparent;")

                    total_payment_value.setText(f"{total:,.0f} so'm")

                    remaining_qarz_value.setText(f"{remaining:,.0f} so'm")
                    if remaining <= 0:
                        remaining_qarz_value.setStyleSheet("color: #00c853; font-size: 20px; font-weight: bold;")
                    else:
                        remaining_qarz_value.setStyleSheet("color: #ff6b35; font-size: 20px; font-weight: bold;")

                except Exception as e:
                    print(f"Update mixed error: {e}")

            cash_input.valueChanged.connect(update_mixed_payment)
            card_input.valueChanged.connect(update_mixed_payment)

            # Boshlang'ich holat
            refresh_balance_label()
            payment_combo.setCurrentIndex(0)
            on_payment_changed("💵 Naxt")

            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Qarzni to'lashda xatolik: {str(e)}")
            print(f"❌ Mark debt error: {e}")

    def _confirm_payment_with_type(self, dialog, debt_id, product_name, debt_amount,
                                   payment_combo, cash_input, card_input,
                                   total_payment_label, remaining_value_label, date_input):
        """To'lovni tasdiqlash - kassa tekshiruvi bilan, savdodan BIR MARTA ayiradi"""
        try:
            payment_type_text = payment_combo.currentText()

            if "Naxt + Plastik" in payment_type_text:
                payment_type = "Naxt+Plastik"
                cash_amount = cash_input.value()
                card_amount = card_input.value()
                total_payment = cash_amount + card_amount

                if cash_amount <= 0 or card_amount <= 0:
                    QMessageBox.warning(dialog, "Xatolik",
                        "Naxt+Plastik to'lovida ikkala maydon ham to'ldirilishi kerak!"
                    )
                    return
            elif "Naxt" in payment_type_text:
                payment_type = "Naxt"
                cash_amount = debt_amount
                card_amount = 0
                total_payment = debt_amount
            else:
                payment_type = "Plastik"
                cash_amount = 0
                card_amount = debt_amount
                total_payment = debt_amount

            if total_payment <= 0:
                QMessageBox.warning(dialog, "Xatolik", "To'lov miqdori 0 dan katta bo'lishi kerak!")
                return

            if total_payment > debt_amount:
                QMessageBox.warning(dialog, "Xatolik",
                    f"To'lov miqdori qarzdan katta!\n"
                    f"Qarz: {debt_amount:,.0f} so'm\n"
                    f"To'lov: {total_payment:,.0f} so'm"
                )
                return

            paid_date = date_input.date().toString("yyyy-MM-dd")

            # ===== KASSA TEKSHIRUVI =====
            balance = self.sale_repo.get_cash_card_balance(paid_date)
            available_cash = balance.get('available_cash', 0)
            available_card = balance.get('available_card', 0)

            display_date = date_input.date().toString("dd.MM.yyyy")

            if cash_amount > available_cash:
                QMessageBox.warning(
                    dialog, "❌ Kassada pul yo'q",
                    f"{display_date} kunida naqd pul yetarli emas!\n\n"
                    f"💵 Kerak: {cash_amount:,.0f} so'm\n"
                    f"💵 Mavjud: {available_cash:,.0f} so'm\n\n"
                    f"Boshqa kunni tanlang yoki to'lov turini o'zgartiring."
                )
                return

            if card_amount > available_card:
                QMessageBox.warning(
                    dialog, "❌ Kassada pul yo'q",
                    f"{display_date} kunida plastik tushum yetarli emas!\n\n"
                    f"💳 Kerak: {card_amount:,.0f} so'm\n"
                    f"💳 Mavjud: {available_card:,.0f} so'm\n\n"
                    f"Boshqa kunni tanlang yoki to'lov turini o'zgartiring."
                )
                return

            # ===== QARZNI TO'LASH =====
            result = self.purchase_repo.mark_as_partially_paid(
                debt_id, total_payment, paid_date, cash_amount, card_amount
            )

            if not result.get('success'):
                QMessageBox.warning(dialog, "Xatolik", result.get('message', 'To\'lovda xatolik!'))
                return

            # ===== SAVDODAN PUL AYIRISH =====
            from controllers.sale_controller import SaleController
            sale_controller = SaleController()

            sales = sale_controller.get_sales_by_date(paid_date)

            if sales:
                sale_id = sales[0]['id']
                sale_controller.reduce_sale_by_payment(sale_id, total_payment, cash_amount, card_amount)

                print(f"💰 Savdodan yechib olindi: {total_payment:,.0f} so'm")
                print(f"💳 To'lov turi: {payment_type}")
                if payment_type == "Naxt+Plastik":
                    print(f"💵 Naqd: {cash_amount:,.0f} so'm")
                    print(f"💳 Plastik: {card_amount:,.0f} so'm")
            else:
                print(f"⚠️ {paid_date} kuni savdo yo'q! Faqat qarz yangilandi.")

            main_window = self.window()
            if hasattr(main_window, 'dashboard'):
                main_window.dashboard.load_data()
            if hasattr(main_window, 'update_all_dots'):
                main_window.update_all_dots()

            msg = f"✅ Qarz to'landi!\n"
            msg += f"💰 To'langan: {total_payment:,.0f} so'm\n"
            msg += f"💳 To'lov turi: {payment_type}\n"
            if payment_type == "Naxt+Plastik":
                msg += f"💵 Naqd: {cash_amount:,.0f} so'm\n"
                msg += f"💳 Plastik: {card_amount:,.0f} so'm"
            elif payment_type == "Naxt":
                msg += f"💵 Naqd: {cash_amount:,.0f} so'm"
            else:
                msg += f"💳 Plastik: {card_amount:,.0f} so'm"

            QMessageBox.information(dialog, "Muvaffaqiyat", msg)
            dialog.accept()
            self.load_debts()
            self.load_inventory_data()
            self.update_main_window_dots()

        except Exception as e:
            QMessageBox.critical(dialog, "Xatolik", f"To'lovda xatolik: {str(e)}")
            print(f"❌ Confirm pay error: {e}")
    
    # ============================================================
    # FIRMALAR
    # ============================================================
    def load_firms(self):
        try:
            firms = self.firm_controller.get_all()
            
            self.firms_table.setRowCount(len(firms))
            
            for i, firm in enumerate(firms):
                self.firms_table.setItem(i, 0, QTableWidgetItem(str(firm['id'])))
                self.firms_table.setItem(i, 1, QTableWidgetItem(firm['name']))
                self.firms_table.setItem(i, 2, QTableWidgetItem(firm.get('phone', '-')))
                
                debt = firm.get('total_debt', 0)
                debt_item = QTableWidgetItem(f"{debt:,.0f} so'm")
                if debt > 0:
                    debt_item.setForeground(QColor(255, 150, 0))
                else:
                    debt_item.setForeground(QColor(0, 200, 0))
                self.firms_table.setItem(i, 3, debt_item)
                
                self.firms_table.setItem(i, 4, QTableWidgetItem(firm.get('address', '-')))
                
                debts = self.debt_repo.get_by_firm(firm['id'])
                self.firms_table.setItem(i, 5, QTableWidgetItem(str(len(debts))))
            
            self.firms_table.resizeColumnsToContents()
            print(f"✅ {len(firms)} ta firma yuklandi")
            
        except Exception as e:
            print(f"❌ Firmalarni yuklashda xatolik: {e}")
    
    def check_firms(self):
        try:
            firms = self.firm_controller.get_all()
            
            if not firms:
                QMessageBox.warning(self, "Ma'lumot", "❌ Hech qanday firma topilmadi!\n\nIltimos, avval firma qo'shing.")
                return
            
            msg = "📋 FIRMALAR RO'YXATI\n"
            msg += "═" * 40 + "\n\n"
            
            for firm in firms:
                firm_id = firm.get('id', 0)
                name = firm.get('name', 'Noma\'lum')
                phone = firm.get('phone', '-')
                debt = firm.get('total_debt', 0)
                address = firm.get('address', '-')
                
                debts = self.debt_repo.get_by_firm(firm_id)
                debt_count = len(debts)
                
                msg += f"🏢 ID: {firm_id}\n"
                msg += f"   Nomi: {name}\n"
                msg += f"   Telefon: {phone}\n"
                msg += f"   Manzil: {address}\n"
                msg += f"   💳 Jami qarz: {debt:,.0f} so'm\n"
                msg += f"   📋 Qarzlar soni: {debt_count} ta\n"
                msg += "\n" + "─" * 30 + "\n\n"
            
            msg += f"📊 Jami firmalar: {len(firms)} ta"
            
            dialog = QDialog(self)
            dialog.setWindowTitle("🔍 Firmalarni tekshirish")
            dialog.setFixedSize(600, 550)
            dialog.setStyleSheet(DARK_STYLE)
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(25, 25, 25, 25)
            
            title = QLabel("🔍 Firmalar ma'lumoti")
            title.setStyleSheet("font-size: 20px; font-weight: bold; color: #6c63ff;")
            layout.addWidget(title)
            
            text = QTextEdit()
            text.setPlainText(msg)
            text.setReadOnly(True)
            text.setFont(QFont("Courier New", 11))
            text.setStyleSheet("""
                QTextEdit {
                    background: #1a1a2e;
                    border: 2px solid #2a2a4a;
                    border-radius: 10px;
                    padding: 15px;
                    color: #e0e0e0;
                }
            """)
            layout.addWidget(text)
            
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            
            close_btn = QPushButton("❌ Yopish")
            close_btn.setObjectName("dangerButton")
            close_btn.setMinimumHeight(40)
            close_btn.setMinimumWidth(120)
            close_btn.clicked.connect(dialog.accept)
            btn_layout.addWidget(close_btn)
            
            layout.addLayout(btn_layout)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Firmalarni tekshirishda xatolik: {str(e)}")
            print(f"❌ Check firms error: {e}")
    
    def show_add_firm_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("➕ Yangi firma qo'shish")
        dialog.setFixedSize(550, 500)
        dialog.setStyleSheet(DARK_STYLE)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Firma nomi")
        name_input.setMinimumHeight(40)
        name_input.setMinimumWidth(350)
        name_input.setStyleSheet("""
            QLineEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 10px 15px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        form_layout.addRow("Nomi:", name_input)
        
        phone_input = QLineEdit()
        phone_input.setPlaceholderText("+998 99 123 45 67")
        phone_input.setMinimumHeight(40)
        phone_input.setMinimumWidth(350)
        phone_input.setStyleSheet("""
            QLineEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 10px 15px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        form_layout.addRow("Telefon:", phone_input)
        
        address_input = QLineEdit()
        address_input.setPlaceholderText("Manzil")
        address_input.setMinimumHeight(40)
        address_input.setMinimumWidth(350)
        address_input.setStyleSheet("""
            QLineEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 10px 15px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        form_layout.addRow("Manzil:", address_input)
        
        note_input = QTextEdit()
        note_input.setMaximumHeight(80)
        note_input.setMinimumWidth(350)
        note_input.setPlaceholderText("Qo'shimcha ma'lumot...")
        note_input.setStyleSheet("""
            QTextEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 10px 15px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        form_layout.addRow("Izoh:", note_input)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        save_btn = QPushButton("💾 Saqlash")
        save_btn.setObjectName("successButton")
        save_btn.setMinimumHeight(40)
        save_btn.setMinimumWidth(120)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Bekor qilish")
        cancel_btn.setObjectName("dangerButton")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        def save_firm():
            name = name_input.text().strip()
            if not name:
                QMessageBox.warning(dialog, "Xatolik", "Iltimos, firma nomini kiriting!")
                return
            
            firm_data = {
                'name': name,
                'phone': phone_input.text().strip(),
                'address': address_input.text().strip(),
                'note': note_input.toPlainText().strip(),
                'total_debt': 0
            }
            
            result = self.firm_controller.create(firm_data)
            if result:
                QMessageBox.information(dialog, "Muvaffaqiyat", "✅ Firma muvaffaqiyatli qo'shildi!")
                dialog.accept()
                self.load_firms()
                self.load_inventory_data()
            else:
                QMessageBox.warning(dialog, "Xatolik", "Firma qo'shishda xatolik!")
        
        save_btn.clicked.connect(save_firm)
        dialog.exec()
    
    def show_add_debt_dialog(self):
        try:
            firms = self.firm_controller.get_all()
            if not firms:
                QMessageBox.warning(self, "Ogohlantirish", "Iltimos, avval firma qo'shing!")
                return
            
            dialog = QDialog(self)
            dialog.setWindowTitle("💰 Firmaga qarz qo'shish")
            dialog.setFixedSize(620, 700)
            dialog.setStyleSheet(DARK_STYLE)
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(25, 25, 25, 25)
            
            firm_label = QLabel("🏢 Firma tanlang:")
            firm_label.setStyleSheet("color: #a0a0b8; font-size: 13px;")
            layout.addWidget(firm_label)
            
            firm_combo = QComboBox()
            firm_combo.setMinimumHeight(40)
            firm_combo.setMinimumWidth(500)
            firm_combo.setStyleSheet("""
                QComboBox {
                    background: #14142a;
                    border: 2px solid #2a2a4a;
                    border-radius: 8px;
                    padding: 10px 15px;
                    color: #e0e0e0;
                    font-size: 14px;
                }
                QComboBox:focus {
                    border: 2px solid #6c63ff;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox QAbstractItemView {
                    background: #1a1a2e;
                    color: #e0e0e0;
                    selection-background-color: #4a4a8a;
                }
            """)
            
            for firm in firms:
                firm_id = firm.get('id', 0)
                firm_name = firm.get('name', 'Noma\'lum')
                debt = firm.get('total_debt', 0)
                debts = self.debt_repo.get_by_firm(firm_id)
                debt_count = len(debts)
                
                if debt > 0:
                    firm_combo.addItem(
                        f"🏢 {firm_name}  |  💳 {debt:,.0f} so'm  |  📋 {debt_count} ta", 
                        firm_id
                    )
                else:
                    firm_combo.addItem(
                        f"🏢 {firm_name}  |  📋 {debt_count} ta", 
                        firm_id
                    )
            layout.addWidget(firm_combo)
            
            layout.addSpacing(5)
            
            type_label = QLabel("📌 Amal turi:")
            type_label.setStyleSheet("color: #a0a0b8; font-size: 13px;")
            layout.addWidget(type_label)
            
            debt_type_combo = QComboBox()
            debt_type_combo.addItems(["📝 Qarz oldim (yetkazib beruvchidan)", "✅ Qarz to'ladim"])
            debt_type_combo.setMinimumHeight(40)
            debt_type_combo.setMinimumWidth(500)
            debt_type_combo.setStyleSheet("""
                QComboBox {
                    background: #14142a;
                    border: 2px solid #2a2a4a;
                    border-radius: 8px;
                    padding: 10px 15px;
                    color: #e0e0e0;
                    font-size: 14px;
                }
                QComboBox:focus {
                    border: 2px solid #6c63ff;
                }
                QComboBox::drop-down {
                    border: none;
                }
            """)
            layout.addWidget(debt_type_combo)
            
            layout.addSpacing(5)
            
            amount_label = QLabel("💰 Miqdor:")
            amount_label.setStyleSheet("color: #a0a0b8; font-size: 13px;")
            layout.addWidget(amount_label)
            
            amount_input = QDoubleSpinBox()
            amount_input.setRange(0, 1000000000)
            amount_input.setPrefix("so'm ")
            amount_input.setMinimumHeight(40)
            amount_input.setMinimumWidth(500)
            amount_input.setStyleSheet("""
                QDoubleSpinBox {
                    background: #14142a;
                    border: 2px solid #2a2a4a;
                    border-radius: 8px;
                    padding: 10px 15px;
                    color: #e0e0e0;
                    font-size: 16px;
                    font-weight: bold;
                }
                QDoubleSpinBox:focus {
                    border: 2px solid #6c63ff;
                }
            """)
            layout.addWidget(amount_input)
            
            layout.addSpacing(5)
            
            desc_label = QLabel("📝 Izoh (ixtiyoriy):")
            desc_label.setStyleSheet("color: #a0a0b8; font-size: 13px;")
            layout.addWidget(desc_label)
            
            desc_input = QTextEdit()
            desc_input.setMaximumHeight(80)
            desc_input.setMinimumWidth(500)
            desc_input.setPlaceholderText("Qo'shimcha ma'lumot...")
            desc_input.setStyleSheet("""
                QTextEdit {
                    background: #14142a;
                    border: 2px solid #2a2a4a;
                    border-radius: 8px;
                    padding: 10px 15px;
                    color: #e0e0e0;
                    font-size: 14px;
                }
                QTextEdit:focus {
                    border: 2px solid #6c63ff;
                }
            """)
            layout.addWidget(desc_input)
            
            date_label = QLabel("📅 Sana:")
            date_label.setStyleSheet("color: #a0a0b8; font-size: 13px;")
            layout.addWidget(date_label)
            
            date_input = QDateEdit()
            date_input.setDate(QDate.currentDate())
            date_input.setCalendarPopup(True)
            date_input.setDisplayFormat("dd.MM.yyyy")
            date_input.setMinimumHeight(40)
            date_input.setMinimumWidth(500)
            date_input.setStyleSheet("""
                QDateEdit {
                    background: #14142a;
                    border: 2px solid #2a2a4a;
                    border-radius: 8px;
                    padding: 10px 15px;
                    color: #e0e0e0;
                    font-size: 14px;
                }
                QDateEdit:focus {
                    border: 2px solid #6c63ff;
                }
            """)
            layout.addWidget(date_input)
            
            layout.addSpacing(10)
            
            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(10)
            
            save_btn = QPushButton("💾 Saqlash")
            save_btn.setObjectName("successButton")
            save_btn.setMinimumHeight(45)
            save_btn.setMinimumWidth(130)
            btn_layout.addWidget(save_btn)
            
            cancel_btn = QPushButton("❌ Bekor qilish")
            cancel_btn.setObjectName("dangerButton")
            cancel_btn.setMinimumHeight(45)
            cancel_btn.setMinimumWidth(130)
            cancel_btn.clicked.connect(dialog.reject)
            btn_layout.addWidget(cancel_btn)
            
            layout.addLayout(btn_layout)
            
            def save_debt():
                firm_id = firm_combo.currentData()
                if not firm_id:
                    QMessageBox.warning(dialog, "Xatolik", "Iltimos, firma tanlang!")
                    return
                
                firm_data = self.firm_controller.get_by_id(firm_id)
                if not firm_data:
                    QMessageBox.warning(dialog, "Xatolik", "Firma ma'lumotlari topilmadi!")
                    return
                
                firm_name = firm_data.get('name', 'Noma\'lum')
                firm_phone = firm_data.get('phone', '-')
                firm_address = firm_data.get('address', '-')
                
                amount = amount_input.value()
                if amount <= 0:
                    QMessageBox.warning(dialog, "Xatolik", "Iltimos, qarz miqdorini kiriting!")
                    return
                
                debt_type = "qarz" if debt_type_combo.currentIndex() == 0 else "to_lov"
                description = desc_input.toPlainText().strip()
                if not description:
                    description = "Qarz" if debt_type == "qarz" else "Qarz to'lovi"
                
                date_str = date_input.date().toString("yyyy-MM-dd")
                description += f" ({date_str})"
                
                result = self.debt_repo.create(firm_id, amount, description, debt_type, firm_name)
                
                if result:
                    total_debt = self.debt_repo.get_total_debt(firm_id)
                    self.firm_controller.update({
                        'id': firm_id,
                        'name': firm_name,
                        'phone': firm_phone,
                        'address': firm_address,
                        'total_debt': total_debt
                    })
                    
                    action_text = "qo'shildi" if debt_type == "qarz" else "to'landi"
                    msg = f"✅ Qarz muvaffaqiyatli {action_text}!\n\n"
                    msg += f"🏢 Firma: {firm_name}\n"
                    msg += f"📞 Telefon: {firm_phone}\n"
                    msg += f"📍 Manzil: {firm_address}\n"
                    msg += f"💳 Yangi qarz: {total_debt:,.0f} so'm"
                    
                    QMessageBox.information(dialog, "Muvaffaqiyat", msg)
                    dialog.accept()
                    self.load_firms()
                    self.load_inventory_data()
                else:
                    QMessageBox.warning(dialog, "Xatolik", "Qarz qo'shishda xatolik!")
            
            save_btn.clicked.connect(save_debt)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Qarz qo'shishda xatolik: {str(e)}")
            print(f"❌ Add debt error: {e}")
    
    def view_firm_details(self, index):
        self.view_firm_details_selected()
    
    def view_firm_details_selected(self):
        try:
            current_row = self.firms_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Ogohlantirish", "Iltimos, firmni tanlang!")
                return
            
            firm_id = int(self.firms_table.item(current_row, 0).text())
            firm_name = self.firms_table.item(current_row, 1).text()
            firm_debt = self.firms_table.item(current_row, 3).text()
            
            firm_debts = self.debt_repo.get_by_firm(firm_id)
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"🏢 {firm_name} - Batafsil")
            dialog.setFixedSize(700, 550)
            dialog.setStyleSheet(DARK_STYLE)
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(25, 25, 25, 25)
            
            info_label = QLabel(f"""
            🏢 Firma: {firm_name}
            💳 Jami qarz: {firm_debt}
            📋 Qarzlar soni: {len(firm_debts)} ta
            """)
            info_label.setStyleSheet("color: #e0e0e0; font-size: 14px; padding: 10px; background: #1a1a2e; border-radius: 8px;")
            layout.addWidget(info_label)
            
            if firm_debts:
                table = QTableWidget()
                table.setColumnCount(5)
                table.setHorizontalHeaderLabels(['Sana', 'Firma', 'Turi', 'Miqdor', 'Izoh'])
                table.setRowCount(len(firm_debts))
                
                for i, debt in enumerate(firm_debts):
                    table.setItem(i, 0, QTableWidgetItem(debt.get('created_at', '')[:16]))
                    debt_firm_name = debt.get('firm_name', firm_name)
                    table.setItem(i, 1, QTableWidgetItem(debt_firm_name))
                    
                    debt_type = debt.get('debt_type', 'qarz')
                    type_text = "📝 Qarz" if debt_type == 'qarz' else "✅ To'lov"
                    table.setItem(i, 2, QTableWidgetItem(type_text))
                    
                    amount = debt.get('amount', 0)
                    amount_item = QTableWidgetItem(f"{amount:,.0f} so'm")
                    if debt_type == 'qarz':
                        amount_item.setForeground(QColor(255, 150, 0))
                    else:
                        amount_item.setForeground(QColor(0, 200, 0))
                    table.setItem(i, 3, amount_item)
                    
                    table.setItem(i, 4, QTableWidgetItem(debt.get('description', '-')))
                
                table.setStyleSheet("""
                    QTableWidget {
                        background: #1a1a2e;
                        border: 2px solid #2a2a4a;
                        border-radius: 8px;
                    }
                    QHeaderView::section {
                        background: #1a1a32;
                        padding: 8px;
                        border: none;
                        border-bottom: 2px solid #2a2a4a;
                        color: #a0a0b8;
                    }
                    QTableWidget::item {
                        padding: 6px;
                        color: #e0e0e0;
                    }
                """)
                layout.addWidget(table)
            else:
                no_debt_label = QLabel("✅ Bu firmaga qarz yo'q!")
                no_debt_label.setStyleSheet("color: #00c853; font-size: 16px; padding: 20px; background: #1a1a2e; border-radius: 8px;")
                no_debt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(no_debt_label)
            
            close_btn = QPushButton("❌ Yopish")
            close_btn.setObjectName("dangerButton")
            close_btn.setMinimumHeight(40)
            close_btn.setMinimumWidth(120)
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.exec()
            
        except Exception as e:
            print(f"❌ Firma batafsil ko'rishda xatolik: {e}")
            QMessageBox.warning(self, "Xatolik", f"Firma ma'lumotlarini ko'rishda xatolik: {str(e)}")
    
    def edit_firm(self):
        try:
            current_row = self.firms_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Ogohlantirish", "Iltimos, tahrirlash uchun firmni tanlang!")
                return
            
            firm_id = int(self.firms_table.item(current_row, 0).text())
            
            firm_data = self.firm_controller.get_by_id(firm_id)
            if not firm_data:
                QMessageBox.warning(self, "Xatolik", "Firma ma'lumotlari topilmadi!")
                return
            
            dialog = QDialog(self)
            dialog.setWindowTitle("✏️ Firmni tahrirlash")
            dialog.setFixedSize(550, 500)
            dialog.setStyleSheet(DARK_STYLE)
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(25, 25, 25, 25)
            
            form_layout = QFormLayout()
            form_layout.setSpacing(12)
            form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
            
            name_input = QLineEdit(firm_data.get('name', ''))
            name_input.setMinimumHeight(40)
            name_input.setMinimumWidth(350)
            name_input.setStyleSheet("""
                QLineEdit {
                    background: #14142a; border: 2px solid #2a2a4a; border-radius: 8px;
                    padding: 10px 15px; color: #e0e0e0; font-size: 14px;
                }
                QLineEdit:focus { border: 2px solid #6c63ff; }
            """)
            form_layout.addRow("Nomi:", name_input)
            
            phone_input = QLineEdit(firm_data.get('phone', ''))
            phone_input.setMinimumHeight(40)
            phone_input.setMinimumWidth(350)
            phone_input.setStyleSheet("""
                QLineEdit {
                    background: #14142a; border: 2px solid #2a2a4a; border-radius: 8px;
                    padding: 10px 15px; color: #e0e0e0; font-size: 14px;
                }
                QLineEdit:focus { border: 2px solid #6c63ff; }
            """)
            form_layout.addRow("Telefon:", phone_input)
            
            address_input = QLineEdit(firm_data.get('address', ''))
            address_input.setMinimumHeight(40)
            address_input.setMinimumWidth(350)
            address_input.setStyleSheet("""
                QLineEdit {
                    background: #14142a; border: 2px solid #2a2a4a; border-radius: 8px;
                    padding: 10px 15px; color: #e0e0e0; font-size: 14px;
                }
                QLineEdit:focus { border: 2px solid #6c63ff; }
            """)
            form_layout.addRow("Manzil:", address_input)
            
            note_input = QTextEdit()
            note_input.setText(firm_data.get('note', ''))
            note_input.setMaximumHeight(80)
            note_input.setMinimumWidth(350)
            note_input.setStyleSheet("""
                QTextEdit {
                    background: #14142a; border: 2px solid #2a2a4a; border-radius: 8px;
                    padding: 10px 15px; color: #e0e0e0; font-size: 14px;
                }
                QTextEdit:focus { border: 2px solid #6c63ff; }
            """)
            form_layout.addRow("Izoh:", note_input)
            
            layout.addLayout(form_layout)
            
            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(10)
            
            save_btn = QPushButton("💾 Saqlash")
            save_btn.setObjectName("successButton")
            save_btn.setMinimumHeight(40)
            save_btn.setMinimumWidth(120)
            btn_layout.addWidget(save_btn)
            
            cancel_btn = QPushButton("❌ Bekor qilish")
            cancel_btn.setObjectName("dangerButton")
            cancel_btn.setMinimumHeight(40)
            cancel_btn.setMinimumWidth(120)
            cancel_btn.clicked.connect(dialog.reject)
            btn_layout.addWidget(cancel_btn)
            
            layout.addLayout(btn_layout)
            
            def save_firm():
                name = name_input.text().strip()
                if not name:
                    QMessageBox.warning(dialog, "Xatolik", "Iltimos, firma nomini kiriting!")
                    return
                
                update_data = {
                    'id': firm_id,
                    'name': name,
                    'phone': phone_input.text().strip(),
                    'address': address_input.text().strip(),
                    'note': note_input.toPlainText().strip(),
                    'total_debt': firm_data.get('total_debt', 0)
                }
                
                result = self.firm_controller.update(update_data)
                if result:
                    QMessageBox.information(dialog, "Muvaffaqiyat", "✅ Firma muvaffaqiyatli yangilandi!")
                    dialog.accept()
                    self.load_firms()
                    self.load_inventory_data()
                else:
                    QMessageBox.warning(dialog, "Xatolik", "Firmani yangilashda xatolik!")
            
            save_btn.clicked.connect(save_firm)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Firmani tahrirlashda xatolik: {str(e)}")
            print(f"❌ Edit firm error: {e}")
    
    def delete_firm(self):
        try:
            current_row = self.firms_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Ogohlantirish", "Iltimos, o'chirish uchun firmni tanlang!")
                return
            
            firm_id = int(self.firms_table.item(current_row, 0).text())
            firm_name = self.firms_table.item(current_row, 1).text()
            firm_debt = self.firms_table.item(current_row, 3).text()
            
            if firm_debt != "0 so'm":
                reply = QMessageBox.question(
                    self, "Tasdiqlash",
                    f"'{firm_name}' firmasining qarzi {firm_debt}.\n"
                    f"Firmani o'chirmoqchimisiz?\n\n"
                    f"⚠️ Eslatma: Qarzlar tarixi saqlanadi.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
            else:
                reply = QMessageBox.question(
                    self, "Tasdiqlash",
                    f"'{firm_name}' firmasini o'chirmoqchimisiz?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
            
            if reply == QMessageBox.StandardButton.Yes:
                result = self.firm_controller.delete(firm_id)
                if result:
                    QMessageBox.information(self, "Muvaffaqiyat", "✅ Firma o'chirildi!")
                    self.load_firms()
                    self.load_inventory_data()
                else:
                    QMessageBox.warning(self, "Xatolik", "Firmani o'chirishda xatolik!")
                
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Firmani o'chirishda xatolik: {str(e)}")
            print(f"❌ Delete firm error: {e}")
    
    # ============================================================
    # QO'SHIMCHA
    # ============================================================
    def update_main_window_dots(self):
        try:
            main_window = self.window()
            if hasattr(main_window, 'update_all_dots'):
                main_window.update_all_dots()
                print("✅ Main window dots yangilandi")
        except Exception as e:
            print(f"❌ Dots yangilashda xatolik: {e}")
    
    def load_inventory(self):
        """Ombor ma'lumotlarini qayta yuklash (tashqi chaqiruv uchun)"""
        self.load_inventory_data()
        