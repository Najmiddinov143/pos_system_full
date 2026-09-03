# views/pos_view.py - TO'LIQ TUZATILGAN

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils.styles import DARK_STYLE
from controllers.sale_controller import SaleController
from controllers.product_controller import ProductController
from models.models import Sale, SaleItem
from datetime import datetime
from views.receipt_view import ReceiptDialog


class CommaDoubleSpinBox(QDoubleSpinBox):
    """Oddiy QDoubleSpinBox, lekin klaviaturada '.' bosilsa ham, ',' bosilsa ham
    ikkalasi bir xil o'nlik ajratuvchi sifatida qabul qilinadi (masalan 2.8 yoki 2,8)."""
    def keyPressEvent(self, event):
        if event.text() == '.':
            comma_event = QKeyEvent(
                event.type(), Qt.Key.Key_Comma, event.modifiers(), ','
            )
            super().keyPressEvent(comma_event)
            return
        super().keyPressEvent(event)



class POSView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.sale_controller = SaleController()
        self.product_controller = ProductController()
        self.cart = []
        self.current_till = 1
        self.manual_total_override = False
        self.computed_final_total = 0
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.load_products()
        self.setup_till_shortcuts()
        # 3 ta mustaqil kassa (savatcha) holati - Ctrl+1/2/3 bilan almashtiriladi
        self.tills = {
            1: self.get_form_snapshot(),
            2: self._empty_till_snapshot(),
            3: self._empty_till_snapshot(),
        }
        self.update_till_indicators()
    
    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # ===== LEFT PANEL =====
        left_panel = QWidget()
        left_panel.setFixedWidth(340)
        left_panel.setStyleSheet("background: #14142a; border-radius: 12px; padding: 12px;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)
        
        search_label = QLabel("🔍 Mahsulot qidirish")
        search_label.setStyleSheet("color: #a0a0b8; font-weight: bold; font-size: 13px;")
        left_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Mahsulot nomini yozing...")
        self.search_input.setMinimumHeight(35)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 13px;
            }
            QLineEdit:focus { border: 2px solid #6c63ff; }
        """)
        self.search_input.textChanged.connect(self.search_products)
        left_layout.addWidget(self.search_input)
        
        products_label = QLabel("📦 Mahsulotlar")
        products_label.setStyleSheet("color: #a0a0b8; font-weight: bold; font-size: 13px;")
        left_layout.addWidget(products_label)
        
        self.products_list = QListWidget()
        self.products_list.setStyleSheet("""
            QListWidget {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-radius: 6px;
                margin: 2px 0;
                color: #e0e0e0;
                font-size: 13px;
            }
            QListWidget::item:selected { background: #4a4a8a; color: white; }
            QListWidget::item:hover { background: #2a2a4a; }
        """)
        self.products_list.itemDoubleClicked.connect(self.add_to_cart)
        left_layout.addWidget(self.products_list)
        
        main_layout.addWidget(left_panel)
        
        # ===== RIGHT PANEL =====
        right_panel = QWidget()
        right_panel.setStyleSheet("background: #14142a; border-radius: 12px; padding: 12px;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(10)
        
        cart_header_layout = QHBoxLayout()
        cart_header = QLabel("🛒 Savatcha")
        cart_header.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        cart_header_layout.addWidget(cart_header)
        cart_header_layout.addStretch()
        
        self.till_buttons = {}
        for n in [1, 2, 3]:
            till_btn = QPushButton(f"Kassa {n}")
            till_btn.setCheckable(True)
            till_btn.setFixedHeight(30)
            till_btn.setToolTip(f"Ctrl+{n}")
            till_btn.setStyleSheet("""
                QPushButton {
                    background: #1a1a2e;
                    color: #a0a0b8;
                    border: 2px solid #2a2a4a;
                    border-radius: 6px;
                    padding: 4px 12px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:checked {
                    background: #6c63ff;
                    color: white;
                    border-color: #6c63ff;
                }
                QPushButton:hover { border-color: #6c63ff; }
            """)
            till_btn.clicked.connect(lambda checked, num=n: self.switch_till(num))
            self.till_buttons[n] = till_btn
            cart_header_layout.addWidget(till_btn)
        self.till_buttons[1].setChecked(True)
        
        right_layout.addLayout(cart_header_layout)
        
        # Cart table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(['Mahsulot', 'Narx', 'Miqdor', 'Jami', ''])
        self.cart_table.setStyleSheet("""
            QTableWidget {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                gridline-color: #2a2a4a;
            }
            QTableWidget::item { padding: 4px 8px; color: #e0e0e0; border: none; }
            QTableWidget::item:selected { background: #4a4a8a; color: white; }
            QHeaderView::section {
                background: #1a1a32;
                padding: 6px 8px;
                border: none;
                border-bottom: 2px solid #2a2a4a;
                color: #a0a0b8;
                font-weight: bold;
                font-size: 11px;
            }
            QTableWidget::item { border-bottom: 1px solid #2a2a4a; }
        """)
        self.cart_table.horizontalHeader().setStretchLastSection(False)
        self.cart_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.cart_table.setAlternatingRowColors(True)
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.setMinimumHeight(120)
        right_layout.addWidget(self.cart_table)
        
        # ===== CAR INFO =====
        car_group = QGroupBox("🚗 Avtomobil")
        car_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 6px 12px;
                background: #1a1a2e;
                margin-top: 4px;
            }
            QGroupBox::title { color: #a0a0b8; font-weight: bold; font-size: 12px; padding: 0 8px; }
        """)
        car_layout = QGridLayout(car_group)
        car_layout.setSpacing(4)
        car_layout.setVerticalSpacing(4)
        car_layout.setHorizontalSpacing(8)
        
        # 1-qator
        car_layout.addWidget(QLabel("🚘"), 0, 0)
        self.car_number_input = QLineEdit()
        self.car_number_input.setPlaceholderText("01A123AA")
        self.car_number_input.setMinimumHeight(28)
        self.car_number_input.setStyleSheet("""
            QLineEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e0e0e0;
                font-size: 12px;
                max-height: 28px;
            }
            QLineEdit:focus { border: 2px solid #6c63ff; }
        """)
        car_layout.addWidget(self.car_number_input, 0, 1)
        
        car_layout.addWidget(QLabel("🏎️"), 0, 2)
        self.car_model_input = QLineEdit()
        self.car_model_input.setPlaceholderText("Model")
        self.car_model_input.setMinimumHeight(28)
        self.car_model_input.setStyleSheet("""
            QLineEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e0e0e0;
                font-size: 12px;
                max-height: 28px;
            }
            QLineEdit:focus { border: 2px solid #6c63ff; }
        """)
        car_layout.addWidget(self.car_model_input, 0, 3)
        
        car_layout.addWidget(QLabel("📱"), 0, 4)
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+998...")
        self.phone_input.setMinimumHeight(28)
        self.phone_input.setStyleSheet("""
            QLineEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e0e0e0;
                font-size: 12px;
                max-height: 28px;
            }
            QLineEdit:focus { border: 2px solid #6c63ff; }
        """)
        car_layout.addWidget(self.phone_input, 0, 5)
        
        # 2-qator
        car_layout.addWidget(QLabel("📏"), 1, 0)
        self.current_km_input = QDoubleSpinBox()
        self.current_km_input.setRange(0, 1000000)
        self.current_km_input.setSingleStep(100)
        self.current_km_input.setSuffix(" km")
        self.current_km_input.setMinimumHeight(28)
        self.current_km_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e0e0e0;
                font-size: 12px;
                max-height: 28px;
            }
            QDoubleSpinBox:focus { border: 2px solid #6c63ff; }
        """)
        car_layout.addWidget(self.current_km_input, 1, 1)
        
        car_layout.addWidget(QLabel("🔄"), 1, 2)
        self.next_km_input = QDoubleSpinBox()
        self.next_km_input.setRange(0, 1000000)
        self.next_km_input.setSingleStep(100)
        self.next_km_input.setSuffix(" km")
        self.next_km_input.setMinimumHeight(28)
        self.next_km_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e0e0e0;
                font-size: 12px;
                max-height: 28px;
            }
            QDoubleSpinBox:focus { border: 2px solid #6c63ff; }
        """)
        car_layout.addWidget(self.next_km_input, 1, 3)
        
        car_layout.addWidget(QLabel("📅"), 1, 4)
        self.oil_date_input = QDateEdit()
        self.oil_date_input.setCalendarPopup(True)
        self.oil_date_input.setDate(QDate.currentDate())
        self.oil_date_input.setMinimumHeight(28)
        self.oil_date_input.setStyleSheet("""
            QDateEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e0e0e0;
                font-size: 12px;
                max-height: 28px;
            }
            QDateEdit:focus { border: 2px solid #6c63ff; }
        """)
        car_layout.addWidget(self.oil_date_input, 1, 5)
        
        # 3-qator
        car_layout.addWidget(QLabel("📅 Keyingi:"), 2, 0)
        self.next_oil_date_input = QDateEdit()
        self.next_oil_date_input.setCalendarPopup(True)
        self.next_oil_date_input.setDate(QDate.currentDate().addDays(180))
        self.next_oil_date_input.setMinimumHeight(28)
        self.next_oil_date_input.setStyleSheet("""
            QDateEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e0e0e0;
                font-size: 12px;
                max-height: 28px;
            }
            QDateEdit:focus { border: 2px solid #6c63ff; }
        """)
        car_layout.addWidget(self.next_oil_date_input, 2, 1, 1, 5)
        
        right_layout.addWidget(car_group)
        
        # ===== BONUS =====
        bonus_group = QGroupBox("🎁 Bonus")
        bonus_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 4px 12px;
                background: #1a1a2e;
                margin-top: 4px;
            }
            QGroupBox::title { color: #a0a0b8; font-weight: bold; font-size: 12px; padding: 0 8px; }
        """)
        bonus_layout = QHBoxLayout(bonus_group)
        bonus_layout.setSpacing(8)
        
        bonus_label = QLabel("Bonus:")
        bonus_label.setStyleSheet("color: #a0a0b8; font-size: 12px;")
        bonus_layout.addWidget(bonus_label)
        
        self.bonus_input = QDoubleSpinBox()
        self.bonus_input.setRange(0, 100000000)
        self.bonus_input.setPrefix("so'm ")
        self.bonus_input.setValue(0)
        self.bonus_input.setMinimumHeight(28)
        self.bonus_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e0e0e0;
                font-size: 12px;
                max-height: 28px;
            }
            QDoubleSpinBox:focus { border: 2px solid #6c63ff; }
        """)
        self.bonus_input.valueChanged.connect(self.update_total)
        bonus_layout.addWidget(self.bonus_input)
        
        bonus_percent_label = QLabel("%:")
        bonus_percent_label.setStyleSheet("color: #a0a0b8; font-size: 12px;")
        bonus_layout.addWidget(bonus_percent_label)
        
        self.bonus_percent_input = QDoubleSpinBox()
        self.bonus_percent_input.setRange(0, 100)
        self.bonus_percent_input.setSuffix("%")
        self.bonus_percent_input.setValue(0)
        self.bonus_percent_input.setMinimumHeight(28)
        self.bonus_percent_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e0e0e0;
                font-size: 12px;
                max-height: 28px;
            }
            QDoubleSpinBox:focus { border: 2px solid #6c63ff; }
        """)
        self.bonus_percent_input.valueChanged.connect(self.calc_bonus_from_percent)
        bonus_layout.addWidget(self.bonus_percent_input)
        
        right_layout.addWidget(bonus_group)
        
        # ===== TO'LOV TURI =====
        payment_group = QGroupBox("💳 To'lov")
        payment_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 4px 12px;
                background: #1a1a2e;
                margin-top: 4px;
            }
            QGroupBox::title { color: #a0a0b8; font-weight: bold; font-size: 12px; padding: 0 8px; }
        """)
        payment_layout = QHBoxLayout(payment_group)
        
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["💵 Naxt", "💳 Plastik", "💵💳 Naxt + Plastik", "📝 Nasiya"])
        self.payment_combo.setMinimumHeight(30)
        self.payment_combo.setStyleSheet("""
            QComboBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 6px;
                padding: 4px 12px;
                color: #e0e0e0;
                font-size: 12px;
                max-height: 30px;
            }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #a0a0b8;
            }
        """)
        self.payment_combo.currentTextChanged.connect(self.on_payment_changed)
        payment_layout.addWidget(self.payment_combo)
        
        right_layout.addWidget(payment_group)
        
        # ===== NASIYA =====
        self.debt_group = QGroupBox("📝 Nasiya")
        self.debt_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #f59e0b;
                border-radius: 8px;
                padding: 4px 12px;
                background: #1a1a2e;
                margin-top: 4px;
            }
            QGroupBox::title { color: #f59e0b; font-weight: bold; font-size: 12px; padding: 0 8px; }
        """)
        debt_layout = QHBoxLayout(self.debt_group)
        debt_layout.setSpacing(6)
        
        self.customer_name_input = QLineEdit()
        self.customer_name_input.setPlaceholderText("Mijoz ismi")
        self.customer_name_input.setMinimumHeight(28)
        self.customer_name_input.setStyleSheet("""
            QLineEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e0e0e0;
                font-size: 12px;
                max-height: 28px;
            }
            QLineEdit:focus { border: 2px solid #6c63ff; }
        """)
        debt_layout.addWidget(self.customer_name_input)
        
        self.customer_phone_input = QLineEdit()
        self.customer_phone_input.setPlaceholderText("📱 Telefon")
        self.customer_phone_input.setMinimumHeight(28)
        self.customer_phone_input.setStyleSheet("""
            QLineEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e0e0e0;
                font-size: 12px;
                max-height: 28px;
            }
            QLineEdit:focus { border: 2px solid #6c63ff; }
        """)
        debt_layout.addWidget(self.customer_phone_input)
        
        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDate(QDate.currentDate().addDays(30))
        self.due_date_input.setMinimumHeight(28)
        self.due_date_input.setStyleSheet("""
            QDateEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e0e0e0;
                font-size: 12px;
                max-height: 28px;
            }
            QDateEdit:focus { border: 2px solid #6c63ff; }
        """)
        debt_layout.addWidget(self.due_date_input)
        
        right_layout.addWidget(self.debt_group)
        self.debt_group.setVisible(False)
        
        # ===== NAXT + PLASTIK (ARALASH TO'LOV) =====
        self.mixed_payment_group = QGroupBox("💵💳 Naxt + Plastik bo'lib to'lash")
        self.mixed_payment_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #6c63ff;
                border-radius: 8px;
                padding: 4px 12px;
                background: #1a1a2e;
                margin-top: 4px;
            }
            QGroupBox::title { color: #6c63ff; font-weight: bold; font-size: 12px; padding: 0 8px; }
        """)
        mixed_layout = QHBoxLayout(self.mixed_payment_group)
        mixed_layout.setSpacing(8)
        
        cash_label = QLabel("💵 Naqd:")
        cash_label.setStyleSheet("color: #a0a0b8; font-size: 12px;")
        mixed_layout.addWidget(cash_label)
        
        self.cash_amount_input = QDoubleSpinBox()
        self.cash_amount_input.setRange(0, 1000000000)
        self.cash_amount_input.setSuffix(" so'm")
        self.cash_amount_input.setMinimumHeight(28)
        self.cash_amount_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #14142a; border: 2px solid #2a2a4a; border-radius: 6px;
                padding: 4px 8px; color: #e0e0e0; font-size: 12px; max-height: 28px;
            }
            QDoubleSpinBox:focus { border: 2px solid #6c63ff; }
        """)
        self.cash_amount_input.valueChanged.connect(self.sync_mixed_payment_from_cash)
        mixed_layout.addWidget(self.cash_amount_input)
        
        card_label = QLabel("💳 Plastik:")
        card_label.setStyleSheet("color: #a0a0b8; font-size: 12px;")
        mixed_layout.addWidget(card_label)
        
        self.card_amount_input = QDoubleSpinBox()
        self.card_amount_input.setRange(0, 1000000000)
        self.card_amount_input.setSuffix(" so'm")
        self.card_amount_input.setReadOnly(True)
        self.card_amount_input.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.card_amount_input.setMinimumHeight(28)
        self.card_amount_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #0f0f22; border: 2px solid #2a2a4a; border-radius: 6px;
                padding: 4px 8px; color: #00c853; font-size: 12px; font-weight: bold; max-height: 28px;
            }
        """)
        mixed_layout.addWidget(self.card_amount_input)
        
        right_layout.addWidget(self.mixed_payment_group)
        self.mixed_payment_group.setVisible(False)
        
        # ===== JAMI =====
        totals_group = QGroupBox("💰 Jami")
        totals_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 6px 12px;
                background: #1a1a2e;
                margin-top: 4px;
            }
            QGroupBox::title { color: #a0a0b8; font-weight: bold; font-size: 12px; padding: 0 8px; }
        """)
        totals_layout = QHBoxLayout(totals_group)
        totals_layout.setSpacing(10)
        
        left_total = QWidget()
        left_total_layout = QVBoxLayout(left_total)
        left_total_layout.setSpacing(2)
        left_total_layout.setContentsMargins(0, 0, 0, 0)
        jami_label = QLabel("Jami:")
        jami_label.setStyleSheet("color: #a0a0b8; font-size: 12px;")
        left_total_layout.addWidget(jami_label)
        self.total_label = QLabel("0 so'm")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #6c63ff;")
        left_total_layout.addWidget(self.total_label)
        totals_layout.addWidget(left_total)
        
        mid_total = QWidget()
        mid_total_layout = QVBoxLayout(mid_total)
        mid_total_layout.setSpacing(2)
        mid_total_layout.setContentsMargins(0, 0, 0, 0)
        chegirma_label = QLabel("Chegirma:")
        chegirma_label.setStyleSheet("color: #a0a0b8; font-size: 12px;")
        mid_total_layout.addWidget(chegirma_label)
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setRange(0, 100)
        self.discount_input.setSuffix("%")
        self.discount_input.setValue(0)
        self.discount_input.setMinimumHeight(28)
        self.discount_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e0e0e0;
                font-size: 12px;
                max-height: 28px;
            }
            QDoubleSpinBox:focus { border: 2px solid #6c63ff; }
        """)
        self.discount_input.valueChanged.connect(self.update_total)
        mid_total_layout.addWidget(self.discount_input)
        totals_layout.addWidget(mid_total)
        
        right_total = QWidget()
        right_total_layout = QVBoxLayout(right_total)
        right_total_layout.setSpacing(2)
        right_total_layout.setContentsMargins(0, 0, 0, 0)
        yakuniy_label = QLabel("Yakuniy (tahrirlanadi):")
        yakuniy_label.setStyleSheet("color: #a0a0b8; font-size: 12px;")
        right_total_layout.addWidget(yakuniy_label)
        
        self.final_total_input = QDoubleSpinBox()
        self.final_total_input.setRange(0, 1000000000)
        self.final_total_input.setSuffix(" so'm")
        self.final_total_input.setMinimumHeight(32)
        self.final_total_input.setStyleSheet("""
            QDoubleSpinBox {
                background: transparent;
                border: none;
                font-size: 18px;
                font-weight: bold;
                color: #00c853;
                padding: 0px;
            }
            QDoubleSpinBox:focus {
                color: #ffb300;
            }
        """)
        self.final_total_input.valueChanged.connect(self.on_final_total_edited)
        right_total_layout.addWidget(self.final_total_input)
        totals_layout.addWidget(right_total)
        
        right_layout.addWidget(totals_group)
        
        # ===== TUGMALAR =====
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        sell_btn = QPushButton("💰 Sotish")
        sell_btn.setObjectName("sellButton")
        sell_btn.setMinimumHeight(40)
        sell_btn.setStyleSheet("""
            QPushButton#sellButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00c853, stop: 1 #009624);
                color: white;
                font-weight: bold;
                font-size: 15px;
                padding: 10px;
                border-radius: 8px;
                border: none;
            }
            QPushButton#sellButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00e863, stop: 1 #00a634);
            }
        """)
        sell_btn.clicked.connect(self.process_sale)
        button_layout.addWidget(sell_btn)
        
        clear_btn = QPushButton("🗑️ Tozalash")
        clear_btn.setObjectName("dangerButton")
        clear_btn.setMinimumHeight(40)
        clear_btn.setStyleSheet("""
            QPushButton#dangerButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #d32f2f, stop: 1 #b71c1c);
                color: white;
                font-weight: bold;
                font-size: 15px;
                padding: 10px;
                border-radius: 8px;
                border: none;
            }
            QPushButton#dangerButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #e33f3f, stop: 1 #c72c2c);
            }
        """)
        clear_btn.clicked.connect(self.clear_cart)
        button_layout.addWidget(clear_btn)
        
        right_layout.addLayout(button_layout)
        
        main_layout.addWidget(right_panel)
    
    def load_products(self, search_term=""):
        try:
            products = self.product_controller.get_all(search_term)
            self.products_list.clear()
            for product in products:
                if product['quantity'] > 0.001:
                    item_text = f"{product['name']}  •  {product['sell_price']:,.0f} so'm  •  {product['quantity']} {product['unit']}"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, product)
                    self.products_list.addItem(item)
        except Exception as e:
            print(f"Error loading products: {e}")
    
    def search_products(self):
        self.load_products(self.search_input.text())
    
    def add_to_cart(self, item):
        try:
            product_data = item.data(Qt.ItemDataRole.UserRole)
            if not product_data:
                return
            
            for i, cart_item in enumerate(self.cart):
                if cart_item['product_id'] == product_data['id']:
                    if cart_item['quantity'] < product_data['quantity']:
                        self.cart[i]['quantity'] += 1
                        self.update_cart_table()
                        return
                    else:
                        QMessageBox.warning(self, "Ogohlantirish", "Mahsulot omborda yetarli emas!")
                        return
            
            if product_data['quantity'] > 0.001:
                self.cart.append({
                    'product_id': product_data['id'],
                    'name': product_data['name'],
                    'sell_price': product_data['sell_price'],
                    'cost_price': product_data['cost_price'],
                    'quantity': 1,
                    'max_quantity': product_data['quantity'],
                    'unit': product_data['unit']
                })
                self.update_cart_table()
            else:
                QMessageBox.warning(self, "Ogohlantirish", "Mahsulot omborda mavjud emas!")
        except Exception as e:
            print(f"Error adding to cart: {e}")
    
    def update_cart_table(self):
        try:
            self.cart_table.setRowCount(len(self.cart))
            
            self.cart_table.setColumnWidth(0, 130)
            self.cart_table.setColumnWidth(1, 90)
            self.cart_table.setColumnWidth(2, 160)
            self.cart_table.setColumnWidth(3, 100)
            self.cart_table.setColumnWidth(4, 50)
            
            for i, item in enumerate(self.cart):
                name_item = QTableWidgetItem(item['name'])
                name_item.setForeground(QColor(255, 255, 255))
                name_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                self.cart_table.setItem(i, 0, name_item)
                
                price_item = QTableWidgetItem(f"{item['sell_price']:,.0f} so'm")
                price_item.setForeground(QColor(100, 200, 255))
                price_item.setFont(QFont("Segoe UI", 11))
                self.cart_table.setItem(i, 1, price_item)
                
                quantity_widget = QWidget()
                quantity_layout = QHBoxLayout(quantity_widget)
                quantity_layout.setContentsMargins(2, 0, 2, 0)
                quantity_layout.setSpacing(4)
                
                quantity_spin = CommaDoubleSpinBox()
                # Nuqta o'rniga vergul bilan kiritish (masalan 2,8)
                ru_locale = QLocale(QLocale.Language.Russian, QLocale.Country.Russia)
                ru_locale.setNumberOptions(QLocale.NumberOption.RejectGroupSeparator)
                quantity_spin.setLocale(ru_locale)
                quantity_spin.setRange(0.1, item['max_quantity'])
                quantity_spin.setSingleStep(0.5)
                quantity_spin.setValue(item['quantity'])
                quantity_spin.setMinimumWidth(60)
                quantity_spin.setMaximumWidth(75)
                quantity_spin.setStyleSheet("""
                    QDoubleSpinBox {
                        background: #1a1a2e;
                        border: 2px solid #2a2a4a;
                        border-radius: 4px;
                        padding: 2px 4px;
                        color: #ffffff;
                        font-size: 12px;
                        font-weight: bold;
                        min-height: 26px;
                        max-height: 30px;
                    }
                    QDoubleSpinBox:focus { border: 2px solid #6c63ff; }
                    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                        width: 14px;
                        background: #2a2a4a;
                        border-radius: 2px;
                    }
                """)
                quantity_spin.valueChanged.connect(lambda value, idx=i: self.update_quantity(idx, value))
                quantity_layout.addWidget(quantity_spin)
                
                unit_label = QLabel(item['unit'].upper())
                unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                unit_label.setFixedWidth(40)
                unit_label.setStyleSheet("""
                    QLabel {
                        color: #00e863;
                        font-size: 11px;
                        font-weight: bold;
                        padding: 2px 6px;
                        background: #1a1a2e;
                        border-radius: 4px;
                        border: 1.5px solid #00e863;
                        min-height: 18px;
                    }
                """)
                quantity_layout.addWidget(unit_label)
                quantity_layout.addStretch()
                
                self.cart_table.setCellWidget(i, 2, quantity_widget)
                
                subtotal = item['sell_price'] * item['quantity']
                subtotal_item = QTableWidgetItem(f"{subtotal:,.0f} so'm")
                subtotal_item.setForeground(QColor(255, 215, 0))
                subtotal_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.cart_table.setItem(i, 3, subtotal_item)
                
                remove_btn = QPushButton("✕")
                remove_btn.setFixedSize(32, 32)
                remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                remove_btn.setToolTip("Savatchadan o'chirish")
                remove_btn.setStyleSheet("""
                    QPushButton {
                        background: #dc2626;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 16px;
                        padding: 0px;
                    }
                    QPushButton:hover { background: #f87171; }
                    QPushButton:pressed { background: #b91c1c; }
                """)
                remove_btn.clicked.connect(lambda checked, idx=i: self.remove_from_cart(idx))
                self.cart_table.setCellWidget(i, 4, remove_btn)
                
                self.cart_table.setRowHeight(i, 46)
            
            self.update_total()
            self.update_till_indicators()
            
        except Exception as e:
            print(f"Error updating cart table: {e}")
    
    def update_quantity(self, index, value):
        if index < len(self.cart):
            self.cart[index]['quantity'] = value
            # MUHIM: bu yerda update_cart_table() chaqirilmaydi!
            # update_cart_table() spinboxni qayta yaratib yuboradi, shu sabab
            # foydalanuvchi "2.8" kabi son yozayotganda har bir raqamdan keyin
            # widget qayta tug'ilib, yozish uzilib qolar edi.
            # Shuning uchun faqat shu qatorning summasi va umumiy summani yangilaymiz.
            item = self.cart[index]
            subtotal = item['sell_price'] * item['quantity']
            subtotal_item = self.cart_table.item(index, 3)
            if subtotal_item:
                subtotal_item.setText(f"{subtotal:,.0f} so'm")
            self.update_total()
            self.update_till_indicators()
    
    def remove_from_cart(self, index):
        if 0 <= index < len(self.cart):
            reply = QMessageBox.question(
                self, "O'chirish",
                f"'{self.cart[index]['name']}' mahsulotini savatchadan o'chirmoqchimisiz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.cart.pop(index)
                self.update_cart_table()
    
    def clear_cart(self):
        if self.cart:
            reply = QMessageBox.question(
                self, "Tozalash",
                "Savatchani tozalamoqchimisiz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.cart = []
                self.update_cart_table()
    
    # ===== KASSALAR (Ctrl+1 / Ctrl+2 / Ctrl+3) =====
    def setup_till_shortcuts(self):
        for n in [1, 2, 3]:
            shortcut = QShortcut(QKeySequence(f"Ctrl+{n}"), self)
            shortcut.activated.connect(lambda checked=False, num=n: self.switch_till(num))
    
    def _empty_till_snapshot(self):
        return {
            'cart': [],
            'car_number': '', 'car_model': '', 'phone_number': '',
            'current_km': 0, 'next_km': 0,
            'oil_date': QDate.currentDate(), 'next_oil_date': QDate.currentDate().addDays(180),
            'payment_index': 0,
            'discount': 0, 'bonus': 0, 'bonus_percent': 0,
            'customer_name': '', 'customer_phone': '',
            'due_date': QDate.currentDate().addDays(30),
            'cash_amount': 0, 'card_amount': 0,
        }
    
    def get_form_snapshot(self):
        return {
            'cart': list(self.cart),
            'car_number': self.car_number_input.text(),
            'car_model': self.car_model_input.text(),
            'phone_number': self.phone_input.text(),
            'current_km': self.current_km_input.value(),
            'next_km': self.next_km_input.value(),
            'oil_date': self.oil_date_input.date(),
            'next_oil_date': self.next_oil_date_input.date(),
            'payment_index': self.payment_combo.currentIndex(),
            'discount': self.discount_input.value(),
            'bonus': self.bonus_input.value(),
            'bonus_percent': self.bonus_percent_input.value(),
            'customer_name': self.customer_name_input.text(),
            'customer_phone': self.customer_phone_input.text(),
            'due_date': self.due_date_input.date(),
            'cash_amount': self.cash_amount_input.value(),
            'card_amount': self.card_amount_input.value(),
        }
    
    def apply_form_snapshot(self, snap):
        self.cart = list(snap['cart'])
        self.manual_total_override = False
        self.car_number_input.setText(snap['car_number'])
        self.car_model_input.setText(snap['car_model'])
        self.phone_input.setText(snap['phone_number'])
        self.current_km_input.setValue(snap['current_km'])
        self.next_km_input.setValue(snap['next_km'])
        self.oil_date_input.setDate(snap['oil_date'])
        self.next_oil_date_input.setDate(snap['next_oil_date'])
        self.payment_combo.setCurrentIndex(snap['payment_index'])
        self.discount_input.setValue(snap['discount'])
        self.bonus_input.setValue(snap['bonus'])
        self.bonus_percent_input.setValue(snap['bonus_percent'])
        self.customer_name_input.setText(snap['customer_name'])
        self.customer_phone_input.setText(snap['customer_phone'])
        self.due_date_input.setDate(snap['due_date'])
        self.debt_group.setVisible(self.payment_combo.currentText() == "📝 Nasiya")
        self.mixed_payment_group.setVisible(self.payment_combo.currentText() == "💵💳 Naxt + Plastik")
        self.cash_amount_input.setValue(snap.get('cash_amount', 0))
        self.card_amount_input.setValue(snap.get('card_amount', 0))
        self.update_cart_table()
    
    def switch_till(self, n):
        if n == self.current_till:
            return
        # joriy kassaning holatini saqlab qo'yamiz, keyin tanlangan kassani yuklaymiz
        self.tills[self.current_till] = self.get_form_snapshot()
        self.current_till = n
        self.apply_form_snapshot(self.tills[n])
        for num, btn in self.till_buttons.items():
            btn.setChecked(num == n)
        self.update_till_indicators()
    
    def update_till_indicators(self):
        """Har bir kassa tugmasida savatchadagi mahsulotlar sonini ko'rsatadi (bo'sh/to'liqligini bilish uchun)"""
        if not hasattr(self, 'tills'):
            return
        empty_style = """
            QPushButton {
                background: #1a1a2e; color: #a0a0b8; border: 2px solid #2a2a4a;
                border-radius: 6px; padding: 4px 12px; font-size: 12px; font-weight: bold;
            }
            QPushButton:checked { background: #6c63ff; color: white; border-color: #6c63ff; }
            QPushButton:hover { border-color: #6c63ff; }
        """
        filled_style = """
            QPushButton {
                background: #1a1a2e; color: #ff9800; border: 2px solid #ff9800;
                border-radius: 6px; padding: 4px 12px; font-size: 12px; font-weight: bold;
            }
            QPushButton:checked { background: #6c63ff; color: white; border-color: #6c63ff; }
            QPushButton:hover { border-color: #6c63ff; }
        """
        for n, btn in self.till_buttons.items():
            if n == self.current_till:
                count = len(self.cart)
            else:
                snap = self.tills.get(n)
                count = len(snap['cart']) if snap else 0
            
            if count > 0:
                btn.setText(f"Kassa {n} 🛒{count}")
                btn.setStyleSheet(filled_style)
            else:
                btn.setText(f"Kassa {n}")
                btn.setStyleSheet(empty_style)
    
    def reset_form(self):
        self.apply_form_snapshot(self._empty_till_snapshot())
    
    def calc_bonus_from_percent(self):
        total = sum(item['sell_price'] * item['quantity'] for item in self.cart)
        percent = self.bonus_percent_input.value()
        bonus = total * (percent / 100)
        self.bonus_input.setValue(bonus)
    
    def update_total(self):
        try:
            total = sum(item['sell_price'] * item['quantity'] for item in self.cart)
            discount = self.discount_input.value()
            bonus = self.bonus_input.value()
            final_total = max(0, total * (1 - discount / 100) - bonus)
            self.total_label.setText(f"{total:,.0f} so'm")
            
            # Hisoblangan yakuniy summani eslab qolamiz - "Yakuniy" maydonini
            # kassir qo'lda o'zgartirgan bo'lsa ham, qancha farq borligini bilish uchun
            self.computed_final_total = final_total
            
            if not getattr(self, 'manual_total_override', False):
                self.final_total_input.blockSignals(True)
                self.final_total_input.setValue(final_total)
                self.final_total_input.blockSignals(False)
            
            if self.payment_combo.currentText() == "💵💳 Naxt + Plastik":
                final_total_safe = self.final_total_input.value()
                self.cash_amount_input.setRange(0, final_total_safe if final_total_safe > 0 else 1000000000)
                if self.cash_amount_input.value() > final_total_safe:
                    self.cash_amount_input.setValue(final_total_safe)
                else:
                    self.sync_mixed_payment_from_cash(self.cash_amount_input.value())
        except Exception as e:
            print(f"Error updating total: {e}")
    
    def on_final_total_edited(self, value):
        """Kassir 'Yakuniy' summani qo'lda o'zgartirdi (masalan narx oshgani uchun).
        Farq (qo'lda kiritilgan - hisoblangan) sof foydaga to'g'ridan-to'g'ri qo'shiladi,
        chunki bu qo'shimcha summaga qo'shimcha tannarx sarflanmagan."""
        self.manual_total_override = abs(value - getattr(self, 'computed_final_total', value)) > 0.01
    
    def on_payment_changed(self, text):
        self.debt_group.setVisible(text == "📝 Nasiya")
        is_mixed = text == "💵💳 Naxt + Plastik"
        self.mixed_payment_group.setVisible(is_mixed)
        if is_mixed:
            # Boshlang'ich holatda hammasi naqd deb qo'yamiz, kassir kerakli qismini o'zgartiradi
            total = sum(item['sell_price'] * item['quantity'] for item in self.cart)
            discount = self.discount_input.value()
            bonus = self.bonus_input.value()
            final_total = max(0, total * (1 - discount / 100) - bonus)
            self.cash_amount_input.setRange(0, final_total if final_total > 0 else 1000000000)
            self.cash_amount_input.setValue(final_total)
    
    def sync_mixed_payment_from_cash(self, cash_value):
        total = sum(item['sell_price'] * item['quantity'] for item in self.cart)
        discount = self.discount_input.value()
        bonus = self.bonus_input.value()
        final_total = max(0, total * (1 - discount / 100) - bonus)
        card_value = max(0, final_total - cash_value)
        self.card_amount_input.setValue(card_value)
    
    def process_sale(self):
        try:
            if not self.cart:
                QMessageBox.warning(self, "Ogohlantirish", "Savatcha bo'sh!")
                return
            
            car_number = self.car_number_input.text().strip()
            car_model = self.car_model_input.text().strip()
            phone_number = self.phone_input.text().strip()
            current_km = self.current_km_input.value()
            next_km = self.next_km_input.value()
            oil_date = self.oil_date_input.date().toString("yyyy-MM-dd")
            next_oil_date = self.next_oil_date_input.date().toString("yyyy-MM-dd")
            
            total = sum(item['sell_price'] * item['quantity'] for item in self.cart)
            total_profit = sum((item['sell_price'] - item['cost_price']) * item['quantity'] for item in self.cart)
            discount_percent = self.discount_input.value()
            bonus = self.bonus_input.value()
            
            # Chegirma va bonusni hisobga olgan holda tizim hisoblagan summa
            computed_total = max(0, total * (1 - discount_percent / 100) - bonus)
            
            # Kassir "Yakuniy" maydonini qo'lda o'zgartirgan bo'lishi mumkin
            # (masalan narx oshib qolgani uchun) - shu qiymatni ishlatamiz
            final_total = self.final_total_input.value()
            extra_charge = final_total - computed_total  # qo'lda qo'shilgan/ayirilgan farq
            
            # MUHIM: xom foyda + qo'lda qo'shilgan farq (chunki qo'shimcha summaga
            # qo'shimcha tannarx sarflanmagan - to'g'ridan-to'g'ri foyda).
            # Chegirma/bonus esa Dashboard'da "Sof foyda" hisoblanganda BIR MARTA
            # ayiriladi, shu yerda ayirilmaydi (ikki marta ayirilib ketmasligi uchun).
            final_profit = total_profit + extra_charge
            
            payment_type = self.payment_combo.currentText().replace("💵💳 ", "").replace("💵 ", "").replace("💳 ", "").replace("📝 ", "")
            is_debt = 1 if payment_type == "Nasiya" else 0
            
            cash_amount = 0
            card_amount = 0
            if payment_type == "Naxt":
                cash_amount = final_total
            elif payment_type == "Plastik":
                card_amount = final_total
            elif payment_type == "Naxt + Plastik":
                cash_amount = self.cash_amount_input.value()
                card_amount = self.card_amount_input.value()
                if round(cash_amount + card_amount) != round(final_total):
                    QMessageBox.warning(
                        self, "Xatolik",
                        f"Naqd ({cash_amount:,.0f}) + Plastik ({card_amount:,.0f}) "
                        f"yakuniy summaga ({final_total:,.0f}) teng emas!"
                    )
                    return
                payment_type = "Naxt+Plastik"
            
            car_data = {
                'car_number': car_number,
                'car_model': car_model,
                'phone_number': phone_number,
                'current_km': current_km,
                'next_km': next_km,
                'oil_date': oil_date,
                'next_oil_date': next_oil_date,
                'payment_type': payment_type,
                'is_debt': is_debt,
                'bonus': bonus,
                'discount_percent': discount_percent,
                'customer_name': self.customer_name_input.text().strip() if is_debt else "",
                'customer_phone': self.customer_phone_input.text().strip() if is_debt else "",
                'discount_amount': total * (discount_percent / 100),  # Chegirma summasi
                'cash_amount': cash_amount,
                'card_amount': card_amount,
                'extra_charge': extra_charge
            }
            
            # ===== TASDIQLASH: xato bosib yuborilsa, hali hech narsa yozilmasdan bekor qilish mumkin =====
            items_count = len(self.cart)
            payment_line = f"💳 To'lov turi: {payment_type}"
            if payment_type == "Naxt+Plastik":
                payment_line = f"💳 To'lov turi: Naxt {cash_amount:,.0f} so'm + Plastik {card_amount:,.0f} so'm"
            
            extra_line = ""
            if abs(extra_charge) > 0.01:
                sign = "+" if extra_charge > 0 else ""
                extra_line = f"✏️ Qo'lda o'zgartirilgan: {sign}{extra_charge:,.0f} so'm\n"
            
            confirm_box = QMessageBox(self)
            confirm_box.setWindowTitle("Sotuvni tasdiqlash")
            confirm_box.setIcon(QMessageBox.Icon.Question)
            confirm_box.setText(
                f"🛒 Mahsulotlar: {items_count} ta\n"
                f"💰 Yakuniy summa: {final_total:,.0f} so'm\n"
                f"{extra_line}"
                f"{payment_line}\n\n"
                f"Sotuvni yakunlaysizmi?"
            )
            yes_btn = confirm_box.addButton("✅ Ha, sotish", QMessageBox.ButtonRole.AcceptRole)
            confirm_box.addButton("❌ Bekor qilish", QMessageBox.ButtonRole.RejectRole)
            confirm_box.setDefaultButton(yes_btn)
            confirm_box.exec()
            
            if confirm_box.clickedButton() != yes_btn:
                return  # Bekor qilindi - savatcha va kiritilgan ma'lumotlar saqlanib qoladi
            
            self.finish_sale(final_total, final_profit, car_data)
            
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Xatolik: {str(e)}")
    
    def finish_sale(self, total, profit, car_data):
        try:
            discount_amount = car_data.get('discount_amount', 0)
            
            sale = Sale(
                total_amount=total,
                total_profit=profit,
                discount=discount_amount,  # discount
                user_id=self.user.id,
                car_number=car_data['car_number'],
                car_model=car_data['car_model'],
                phone_number=car_data['phone_number'],
                current_km=car_data['current_km'],
                next_km=car_data['next_km'],
                oil_change_date=car_data['oil_date'],
                next_oil_change_date=car_data['next_oil_date'],
                payment_type=car_data['payment_type'],
                bonus_amount=car_data['bonus'],
                discount_amount=discount_amount,  # discount_amount - MUHIM!
                cash_amount=car_data.get('cash_amount', 0),
                card_amount=car_data.get('card_amount', 0),
                extra_charge=car_data.get('extra_charge', 0),
                is_debt=car_data['is_debt'],
                customer_name=car_data['customer_name'],
                customer_phone=car_data['customer_phone']
            )
            
            sale_items = []
            for item in self.cart:
                sale_item = SaleItem(
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    sell_price=item['sell_price'],
                    cost_price=item['cost_price'],
                    subtotal=item['sell_price'] * item['quantity']
                )
                sale_items.append(sale_item)
            
            sale_id = self.sale_controller.create_sale(sale, sale_items)
            
            receipt_dialog = ReceiptDialog(sale_id, self, car_data['payment_type'])
            receipt_dialog.exec()
            
            self.cart = []
            self.reset_form()
            self.load_products()
            
            QMessageBox.information(self, "Muvaffaqiyat", f"✅ Sotuv muvaffaqiyatli amalga oshirildi!\n💳 To'lov turi: {car_data['payment_type']}")
            
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Sotuvni amalga oshirishda xatolik: {str(e)}")