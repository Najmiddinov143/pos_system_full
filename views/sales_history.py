# views/sales_history.py - TO'LIQ TUZATILGAN

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils.styles import DARK_STYLE
from controllers.sale_controller import SaleController
from models.repositories import PurchaseRepository, SaleRepository
from datetime import datetime, timedelta

class SalesHistory(QWidget):
    def __init__(self):
        super().__init__()
        self.sale_controller = SaleController()
        self.purchase_repo = PurchaseRepository()
        self.sale_repo = SaleRepository()
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.load_sales()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #1a1a2e, stop: 1 #2a2a4a);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        
        title = QLabel("📋 Savdo tarixi")
        title.setObjectName("titleLabel")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Sana filtri
        date_layout = QHBoxLayout()
        date_layout.setSpacing(10)
        
        date_layout.addWidget(QLabel("📅 Sana:"))
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setFixedWidth(120)
        self.start_date.setStyleSheet("""
            QDateEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 5px 10px;
                color: #e0e0e0;
            }
        """)
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("dan"))
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setFixedWidth(120)
        self.end_date.setStyleSheet("""
            QDateEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 5px 10px;
                color: #e0e0e0;
            }
        """)
        date_layout.addWidget(self.end_date)
        
        filter_btn = QPushButton("🔍 Filtr")
        filter_btn.setObjectName("primaryButton")
        filter_btn.clicked.connect(self.load_sales)
        date_layout.addWidget(filter_btn)
        
        header_layout.addLayout(date_layout)
        
        refresh_btn = QPushButton("🔄 Yangilash")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.clicked.connect(self.load_sales)
        header_layout.addWidget(refresh_btn)
        
        layout.addWidget(header_widget)
        
        # Stats
        stats_layout = QHBoxLayout()
        self.stats_labels = {}
        stats = [
            ("💰 Jami sotuv", "total", "0 so'm", "#6c63ff"),
            ("📊 Jami foyda", "profit", "0 so'm", "#00c853"),
            ("📝 Sotuvlar soni", "count", "0", "#ff9800")
        ]
        
        for label, key, default, color in stats:
            group = QGroupBox(label)
            group.setStyleSheet(f"""
                QGroupBox {{
                    background: #1a1a2e;
                    border: 2px solid {color};
                    border-radius: 12px;
                    padding: 10px;
                }}
                QGroupBox::title {{
                    color: #a0a0b8;
                    font-weight: bold;
                    padding: 0 10px;
                }}
            """)
            group_layout = QVBoxLayout(group)
            label_widget = QLabel(default)
            label_widget.setObjectName("cardValue")
            label_widget.setStyleSheet(f"font-size: 24px; color: {color}; font-weight: bold;")
            label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            group_layout.addWidget(label_widget)
            stats_layout.addWidget(group)
            self.stats_labels[key] = label_widget
        
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
        
        # TAB 1: SOTUVLAR
        sales_tab = QWidget()
        sales_layout = QVBoxLayout(sales_tab)
        sales_layout.setContentsMargins(10, 10, 10, 10)
        
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(10)
        self.sales_table.setHorizontalHeaderLabels([
            'ID', 'Sana', 'Mashina', 'Model', 'Telefon',
            'Jami', "To'lov turi", 'Chegirma', 'Bonus', 'Holat'
        ])
        self.sales_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sales_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.sales_table.horizontalHeader().setStretchLastSection(True)
        self.sales_table.setStyleSheet("""
            QTableWidget {
                background: #1a1a2e;
                border: none;
                border-radius: 10px;
                gridline-color: #2a2a4a;
            }
            QHeaderView::section {
                background: #1a1a32;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #2a2a4a;
                color: #a0a0b8;
                font-weight: bold;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px;
                color: #e0e0e0;
                font-size: 13px;
                border-bottom: 1px solid #2a2a4a;
            }
            QTableWidget::item:selected {
                background: #4a4a8a;
                color: white;
            }
        """)
        self.sales_table.verticalHeader().setVisible(False)
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.setColumnWidth(0, 50)
        self.sales_table.setColumnWidth(1, 120)
        self.sales_table.setColumnWidth(2, 130)
        self.sales_table.setColumnWidth(3, 150)
        self.sales_table.setColumnWidth(4, 120)
        self.sales_table.setColumnWidth(5, 120)
        self.sales_table.setColumnWidth(6, 120)
        self.sales_table.setColumnWidth(7, 80)
        self.sales_table.setColumnWidth(8, 80)
        self.sales_table.setColumnWidth(9, 100)
        sales_layout.addWidget(self.sales_table)
        
        self.tab_widget.addTab(sales_tab, "📋 Sotuvlar")
        
        # TAB 2: QARZDORLAR (Mijozlar bizdan Nasiyaga olgan)
        debtors_tab = QWidget()
        debtors_layout = QVBoxLayout(debtors_tab)
        debtors_layout.setContentsMargins(10, 10, 10, 10)
        
        self.debtors_table = QTableWidget()
        self.debtors_table.setColumnCount(6)
        self.debtors_table.setHorizontalHeaderLabels([
            'ID', 'Mijoz', 'Telefon', 'Mashina', 'Qarz', 'Sana'
        ])
        self.debtors_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.debtors_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.debtors_table.horizontalHeader().setStretchLastSection(True)
        self.debtors_table.setStyleSheet("""
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
        """)
        self.debtors_table.verticalHeader().setDefaultSectionSize(50)
        debtors_layout.addWidget(self.debtors_table)
        
        self.tab_widget.addTab(debtors_tab, "💳 Qarzdorlar")
        
        # TAB 3: QARZ BERGANLAR (Biz yetkazib beruvchidan Nasiyaga olgan)
        creditors_tab = QWidget()
        creditors_layout = QVBoxLayout(creditors_tab)
        creditors_layout.setContentsMargins(10, 10, 10, 10)
        
        self.creditors_table = QTableWidget()
        self.creditors_table.setColumnCount(6)
        self.creditors_table.setHorizontalHeaderLabels([
            'ID', 'Mahsulot', 'Miqdor', 'Qarz', 'Sana', "To'lov muddati"
        ])
        self.creditors_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.creditors_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.creditors_table.horizontalHeader().setStretchLastSection(True)
        self.creditors_table.setStyleSheet("""
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
        """)
        self.creditors_table.verticalHeader().setDefaultSectionSize(50)
        creditors_layout.addWidget(self.creditors_table)
        
        self.tab_widget.addTab(creditors_tab, "📝 Qarz berganlar")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.change_payment_btn = QPushButton("💳 To'lov turini o'zgartirish")
        self.change_payment_btn.setObjectName("primaryButton")
        self.change_payment_btn.setMinimumHeight(40)
        self.change_payment_btn.clicked.connect(self.change_payment_type)
        button_layout.addWidget(self.change_payment_btn)
        
        view_btn = QPushButton("👁️ Batafsil")
        view_btn.setObjectName("primaryButton")
        view_btn.setMinimumHeight(40)
        view_btn.clicked.connect(self.view_sale_details)
        button_layout.addWidget(view_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def load_sales(self):
        """Savdo tarixini yuklash"""
        try:
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")
            
            sales = self.sale_controller.get_sales_by_date_range(start_date, end_date)
            
            self.sales_table.setRowCount(0)
            
            if not sales:
                self.sales_table.setRowCount(1)
                empty_item = QTableWidgetItem("📭 Savdo tarixi bo'sh")
                empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                empty_item.setForeground(QColor(160, 160, 184))
                self.sales_table.setItem(0, 0, empty_item)
                self.sales_table.setSpan(0, 0, 1, 10)
                self.sales_table.setRowHeight(0, 50)
                
                self.stats_labels['total'].setText("0 so'm")
                self.stats_labels['profit'].setText("0 so'm")
                self.stats_labels['count'].setText("0")
                
                self.load_debtors(start_date, end_date)
                self.load_creditors(start_date, end_date)
                return
            
            total_amount = 0
            
            self.sales_table.setRowCount(len(sales))
            
            for i, sale in enumerate(sales):
                id_item = QTableWidgetItem(str(sale.get('id', '')))
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.sales_table.setItem(i, 0, id_item)
                
                self.sales_table.setItem(i, 1, QTableWidgetItem(sale.get('created_at', '')))
                self.sales_table.setItem(i, 2, QTableWidgetItem(sale.get('car_number', '-')))
                self.sales_table.setItem(i, 3, QTableWidgetItem(sale.get('car_model', '-')))
                self.sales_table.setItem(i, 4, QTableWidgetItem(sale.get('phone_number', '-')))
                
                amount = sale.get('total_amount', 0)
                total_amount += amount
                self.sales_table.setItem(i, 5, QTableWidgetItem(f"{amount:,.0f} so'm"))
                
                payment_type = sale.get('payment_type', 'Naxt')
                payment_item = QTableWidgetItem(payment_type)
                if payment_type == 'Naxt':
                    payment_item.setForeground(QColor(0, 200, 0))
                elif payment_type == 'Plastik':
                    payment_item.setForeground(QColor(0, 150, 255))
                else:
                    payment_item.setForeground(QColor(255, 150, 0))
                self.sales_table.setItem(i, 6, payment_item)
                
                discount = sale.get('discount_amount', 0) or 0
                self.sales_table.setItem(i, 7, QTableWidgetItem(f"{discount:,.0f} so'm"))
                
                bonus = sale.get('bonus_amount', 0) or 0
                self.sales_table.setItem(i, 8, QTableWidgetItem(f"{bonus:,.0f} so'm"))
                
                is_debt = sale.get('is_debt', 0)
                debt_paid = sale.get('debt_paid', 0)
                if is_debt:
                    if debt_paid:
                        status = "✅ To'langan"
                        status_color = QColor(0, 200, 0)
                    else:
                        status = "⏳ Qarzdor"
                        status_color = QColor(255, 150, 0)
                else:
                    status = "✅ To'langan"
                    status_color = QColor(0, 200, 0)
                
                status_item = QTableWidgetItem(status)
                status_item.setForeground(status_color)
                self.sales_table.setItem(i, 9, status_item)
            
            self.stats_labels['total'].setText(f"{total_amount:,.0f} so'm")
            self.stats_labels['count'].setText(str(len(sales)))
            
            profit = sum(s.get('total_profit', 0) for s in sales)
            self.stats_labels['profit'].setText(f"{profit:,.0f} so'm")
            
            self.sales_table.resizeColumnsToContents()
            print(f"✅ {len(sales)} ta savdo yuklandi")
            
            self.load_debtors(start_date, end_date)
            self.load_creditors(start_date, end_date)
            
        except Exception as e:
            print(f"❌ Error loading sales: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Xatolik", f"Savdo tarixini yuklashda xatolik: {str(e)}")
    
    def load_debtors(self, start_date=None, end_date=None):
        """Qarzdorlarni yuklash"""
        try:
            sales = self.sale_controller.get_sales_by_date_range(start_date, end_date)
            debtors = [s for s in sales if s.get('is_debt', 0) == 1 and s.get('debt_paid', 0) == 0]
            
            self.debtors_table.setRowCount(len(debtors))
            for i, debtor in enumerate(debtors):
                self.debtors_table.setItem(i, 0, QTableWidgetItem(str(debtor.get('id', ''))))
                self.debtors_table.setItem(i, 1, QTableWidgetItem(debtor.get('customer_name', 'Noma\'lum')))
                self.debtors_table.setItem(i, 2, QTableWidgetItem(debtor.get('customer_phone', '-')))
                self.debtors_table.setItem(i, 3, QTableWidgetItem(debtor.get('car_number', '-')))
                self.debtors_table.setItem(i, 4, QTableWidgetItem(f"{debtor.get('total_amount', 0):,.0f} so'm"))
                self.debtors_table.setItem(i, 5, QTableWidgetItem(debtor.get('created_at', '')))
            
            self.debtors_table.resizeColumnsToContents()
            print(f"✅ {len(debtors)} ta qarzdor yuklandi")
            
        except Exception as e:
            print(f"❌ Error loading debtors: {e}")
    
    def load_creditors(self, start_date=None, end_date=None):
        """Qarz berganlarni yuklash"""
        try:
            all_purchases = self.purchase_repo.get_all_purchases()
            creditors = [p for p in all_purchases if p.get('payment_type') == 'Nasiya' and p.get('is_paid', 0) == 0]
            
            if start_date and end_date:
                filtered_creditors = []
                for credit in creditors:
                    credit_date = credit.get('purchase_date', '')
                    if credit_date and start_date <= credit_date <= end_date:
                        filtered_creditors.append(credit)
            else:
                filtered_creditors = creditors
            
            self.creditors_table.setRowCount(len(filtered_creditors))
            for i, credit in enumerate(filtered_creditors):
                self.creditors_table.setItem(i, 0, QTableWidgetItem(str(credit['id'])))
                self.creditors_table.setItem(i, 1, QTableWidgetItem(credit.get('product_name', '')))
                self.creditors_table.setItem(i, 2, QTableWidgetItem(f"{credit['quantity']}"))
                self.creditors_table.setItem(i, 3, QTableWidgetItem(f"{credit['total_cost']:,.0f} so'm"))
                self.creditors_table.setItem(i, 4, QTableWidgetItem(credit.get('purchase_date', '')))
                
                due_date = credit.get('due_date', '')
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
                
                self.creditors_table.setItem(i, 5, QTableWidgetItem(due_date or '-'))
            
            self.creditors_table.resizeColumnsToContents()
            print(f"✅ {len(filtered_creditors)} ta qarz bergan yuklandi")
            
        except Exception as e:
            print(f"❌ Error loading creditors: {e}")
    
    def change_payment_type(self):
        """To'lov turini o'zgartirish"""
        try:
            current_tab_index = self.tab_widget.currentIndex()
            sale_id = None
            current_payment = None
            car_number = None
            
            if current_tab_index == 0:
                current_row = self.sales_table.currentRow()
                if current_row < 0:
                    QMessageBox.warning(self, "Ogohlantirish", "Iltimos, o'zgartirmoqchi bo'lgan savdoni tanlang!")
                    return
                
                sale_id_item = self.sales_table.item(current_row, 0)
                if not sale_id_item:
                    return
                
                sale_id = int(sale_id_item.text())
                current_payment = self.sales_table.item(current_row, 6).text()
                car_number = self.sales_table.item(current_row, 2).text()
                
            elif current_tab_index == 1:
                current_row = self.debtors_table.currentRow()
                if current_row < 0:
                    QMessageBox.warning(self, "Ogohlantirish", "Iltimos, o'zgartirmoqchi bo'lgan qarzdorni tanlang!")
                    return
                
                sale_id_item = self.debtors_table.item(current_row, 0)
                if not sale_id_item:
                    return
                
                sale_id = int(sale_id_item.text())
                current_payment = "Nasiya"
                car_number = self.debtors_table.item(current_row, 3).text()
                
            elif current_tab_index == 2:
                QMessageBox.warning(self, "Ogohlantirish", "Qarz berganlar tabida to'lov turini o'zgartirib bo'lmaydi!")
                return
            
            if not sale_id:
                QMessageBox.warning(self, "Xatolik", "Savdo ID si topilmadi!")
                return
            
            # ===== DIALOG =====
            dialog = QDialog(self)
            dialog.setWindowTitle("💳 To'lov turini o'zgartirish")
            dialog.setFixedWidth(460)
            dialog.setStyleSheet(DARK_STYLE)
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(18)
            layout.setContentsMargins(28, 28, 28, 28)
            
            # ---- Ma'lumot kartochkasi ----
            info_card = QWidget()
            info_card.setStyleSheet("""
                QWidget {
                    background: #1a1a2e;
                    border: 2px solid #2a2a4a;
                    border-radius: 12px;
                }
            """)
            info_card_layout = QVBoxLayout(info_card)
            info_card_layout.setContentsMargins(18, 14, 18, 14)
            info_card_layout.setSpacing(6)

            car_row = QLabel(f"🚗  Mashina: <b style='color:#ffffff;'>{car_number}</b>")
            car_row.setStyleSheet("color: #a0a0b8; font-size: 14px; background: transparent;")
            info_card_layout.addWidget(car_row)

            current_row = QLabel(f"💳  Joriy to'lov: <b style='color:#ffffff;'>{current_payment}</b>")
            current_row.setStyleSheet("color: #a0a0b8; font-size: 14px; background: transparent;")
            info_card_layout.addWidget(current_row)

            layout.addWidget(info_card)

            payment_label = QLabel("Yangi to'lov turini tanlang:")
            payment_label.setStyleSheet("color: #e0e0e0; font-size: 14px; font-weight: bold;")
            layout.addWidget(payment_label)
            
            payment_combo = QComboBox()
            payment_combo.addItems(['💵 Naxt', '💳 Plastik', '📝 Nasiya'])
            combo_map = {'Naxt': '💵 Naxt', 'Plastik': '💳 Plastik', 'Nasiya': '📝 Nasiya'}
            payment_combo.setCurrentText(combo_map.get(current_payment, current_payment))
            payment_combo.setMinimumHeight(42)
            payment_combo.setStyleSheet("""
                QComboBox {
                    background: #1a1a2e;
                    border: 2px solid #2a2a4a;
                    border-radius: 8px;
                    padding: 10px 15px;
                    color: #e0e0e0;
                    font-size: 14px;
                    font-weight: 600;
                }
                QComboBox:focus { border: 2px solid #6c63ff; }
                QComboBox::drop-down { border: none; }
                QComboBox QAbstractItemView {
                    background: #1a1a2e;
                    color: #e0e0e0;
                    selection-background-color: #4a4a8a;
                    padding: 4px;
                }
            """)
            layout.addWidget(payment_combo)
            
            # ---- Nasiya ma'lumotlari (faqat "Nasiya" tanlanganda ko'rinadi) ----
            debt_group = QGroupBox("📝 Nasiya ma'lumotlari")
            debt_group.setStyleSheet("""
                QGroupBox {
                    background: #1f1a14;
                    border: 2px solid #ff9800;
                    border-radius: 12px;
                    margin-top: 12px;
                    padding-top: 16px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 12px;
                    padding: 0 8px;
                    color: #ff9800;
                    font-size: 14px;
                }
            """)
            debt_layout = QVBoxLayout(debt_group)
            debt_layout.setSpacing(12)
            debt_layout.setContentsMargins(16, 10, 16, 16)

            debt_hint = QLabel("Qarzdorlar ro'yxatida ko'rsatish uchun mijoz ma'lumotlarini kiriting:")
            debt_hint.setWordWrap(True)
            debt_hint.setStyleSheet("color: #c9a876; font-size: 12px; font-weight: normal; background: transparent;")
            debt_layout.addWidget(debt_hint)

            name_label = QLabel("👤 Mijoz ismi")
            name_label.setStyleSheet("color: #d0d0e0; font-size: 13px; font-weight: normal; background: transparent;")
            debt_layout.addWidget(name_label)

            customer_name_input = QLineEdit()
            customer_name_input.setPlaceholderText("Masalan: Alisher Karimov")
            customer_name_input.setMinimumHeight(40)
            customer_name_input.setStyleSheet("""
                QLineEdit {
                    background: #14142a;
                    border: 2px solid #3a2f1a;
                    border-radius: 8px;
                    padding: 10px 15px;
                    color: #e0e0e0;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #ff9800;
                }
            """)
            debt_layout.addWidget(customer_name_input)

            phone_label = QLabel("📞 Telefon raqami")
            phone_label.setStyleSheet("color: #d0d0e0; font-size: 13px; font-weight: normal; background: transparent;")
            debt_layout.addWidget(phone_label)
            
            customer_phone_input = QLineEdit()
            customer_phone_input.setPlaceholderText("Masalan: +998 90 123 45 67")
            customer_phone_input.setMinimumHeight(40)
            customer_phone_input.setStyleSheet("""
                QLineEdit {
                    background: #14142a;
                    border: 2px solid #3a2f1a;
                    border-radius: 8px;
                    padding: 10px 15px;
                    color: #e0e0e0;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #ff9800;
                }
            """)
            debt_layout.addWidget(customer_phone_input)
            
            layout.addWidget(debt_group)
            debt_group.setVisible(False)
            
            def on_payment_changed(text):
                debt_group.setVisible('Nasiya' in text)
                dialog.adjustSize()
            
            payment_combo.currentTextChanged.connect(on_payment_changed)
            
            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(10)
            
            save_btn = QPushButton("💾 Saqlash")
            save_btn.setObjectName("successButton")
            save_btn.setMinimumHeight(40)
            btn_layout.addWidget(save_btn)
            
            cancel_btn = QPushButton("❌ Bekor qilish")
            cancel_btn.setObjectName("dangerButton")
            cancel_btn.setMinimumHeight(40)
            cancel_btn.clicked.connect(dialog.reject)
            btn_layout.addWidget(cancel_btn)
            
            layout.addLayout(btn_layout)
            
            def save_payment():
                try:
                    new_payment = payment_combo.currentText().split(" ", 1)[-1].strip()
                    
                    if new_payment == 'Nasiya':
                        customer_name = customer_name_input.text().strip()
                        customer_phone = customer_phone_input.text().strip()
                        if not customer_name:
                            QMessageBox.warning(dialog, "Xatolik", "Iltimos, mijoz ismini kiriting!")
                            return
                        if not customer_phone:
                            QMessageBox.warning(dialog, "Xatolik", "Iltimos, mijoz telefonini kiriting!")
                            return
                    
                    update_data = {
                        'payment_type': new_payment,
                        'is_debt': 1 if new_payment == 'Nasiya' else 0
                    }
                    
                    if new_payment == 'Nasiya':
                        update_data['customer_name'] = customer_name_input.text().strip()
                        update_data['customer_phone'] = customer_phone_input.text().strip()
                    else:
                        update_data['customer_name'] = ''
                        update_data['customer_phone'] = ''
                    
                    result = self.sale_controller.update_sale(sale_id, update_data)
                    
                    if result:
                        QMessageBox.information(dialog, "Muvaffaqiyat", 
                            f"✅ To'lov turi '{current_payment}' dan '{new_payment}' ga o'zgartirildi!")
                        dialog.accept()
                        self.load_sales()
                    else:
                        QMessageBox.warning(dialog, "Xatolik", "To'lov turini o'zgartirishda xatolik yuz berdi!")
                        
                except Exception as e:
                    QMessageBox.critical(dialog, "Xatolik", f"Xatolik: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            save_btn.clicked.connect(save_payment)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Xatolik: {str(e)}")
            print(f"❌ Error changing payment type: {e}")
            import traceback
            traceback.print_exc()
    
    def view_sale_details(self):
        """Savdo detallarini ko'rish - CHEK CHIQARISH"""
        try:
            current_tab_index = self.tab_widget.currentIndex()
            sale_id = None
            
            if current_tab_index == 0:
                current_row = self.sales_table.currentRow()
                if current_row < 0:
                    QMessageBox.warning(self, "Ogohlantirish", "Iltimos, savdoni tanlang!")
                    return
                
                sale_id_item = self.sales_table.item(current_row, 0)
                if sale_id_item:
                    sale_id = int(sale_id_item.text())
                    
            elif current_tab_index == 1:
                current_row = self.debtors_table.currentRow()
                if current_row < 0:
                    QMessageBox.warning(self, "Ogohlantirish", "Iltimos, qarzdorni tanlang!")
                    return
                
                sale_id_item = self.debtors_table.item(current_row, 0)
                if sale_id_item:
                    sale_id = int(sale_id_item.text())
                    
            elif current_tab_index == 2:
                QMessageBox.warning(self, "Ogohlantirish", "Qarz berganlar tabida batafsil ko'rib bo'lmaydi!")
                return
            
            if not sale_id:
                QMessageBox.warning(self, "Xatolik", "Savdo ID si topilmadi!")
                return
            
            from views.receipt_view import ReceiptDialog
            
            sale_data = self.sale_controller.get_sale_by_id(sale_id)
            if not sale_data:
                QMessageBox.warning(self, "Xatolik", "Savdo ma'lumotlari topilmadi!")
                return
            
            payment_type = sale_data.get('payment_type', 'Naxt')
            
            dialog = ReceiptDialog(sale_id, self, payment_type)
            dialog.exec()
            
            print(f"✅ Chek ochildi (ID: {sale_id})")
            
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Chekni ochishda xatolik: {str(e)}")
            print(f"❌ Error viewing sale details: {e}")
            import traceback
            traceback.print_exc()