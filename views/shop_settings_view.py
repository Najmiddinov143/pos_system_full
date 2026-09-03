# views/shop_settings_view.py - TO'LIQ TUZATILGAN

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils.styles import DARK_STYLE
from models.repositories import ShopSettingsRepository, SettingRepository, UserRepository
import bcrypt
import os
import shutil

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        self.shop_repo = ShopSettingsRepository()
        self.setting_repo = SettingRepository()
        self.user_repo = UserRepository()
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # ===== HEADER =====
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #1a1a2e, stop: 1 #2a2a4a);
                border-radius: 15px;
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(25, 10, 25, 10)
        
        title = QLabel("⚙️ Sozlamalar")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: white; background: transparent;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        save_btn = QPushButton("💾 Saqlash")
        save_btn.setObjectName("successButton")
        save_btn.setMinimumSize(160, 45)
        save_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        save_btn.clicked.connect(self.save_settings)
        header_layout.addWidget(save_btn)
        
        layout.addWidget(header_widget)
        
        # ===== TAB WIDGET =====
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 12px;
            }
            QTabBar::tab {
                background: #111122;
                color: #a0a0b8;
                padding: 14px 40px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: #1a1a2e;
                color: #6c63ff;
                border: 2px solid #2a2a4a;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                color: #ffffff;
                background: #161633;
            }
        """)
        layout.addWidget(self.tab_widget)
        
        def create_scroll_tab():
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("QScrollArea { border: none; background: #1a1a2e; }")
            content_widget = QWidget()
            content_widget.setStyleSheet("background: #1a1a2e;")
            scroll.setWidget(content_widget)
            return scroll, content_widget

        # ============================================================
        # TAB 1: DO'KON
        # ============================================================
        shop_scroll, shop_tab = create_scroll_tab()
        shop_layout = QVBoxLayout(shop_tab)
        shop_layout.setContentsMargins(40, 40, 40, 40)
        
        shop_form = QFormLayout()
        shop_form.setSpacing(25)
        shop_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        input_style = """
            QLineEdit, QTextEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 10px;
                padding: 12px 18px;
                color: #e0e0e0;
                font-size: 15px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #6c63ff;
                background: #161633;
            }
            QLabel {
                color: #a0a0b8;
                font-size: 16px;
                font-weight: 500;
            }
        """
        shop_tab.setStyleSheet(input_style)
        
        self.shop_name_input = QLineEdit()
        self.shop_name_input.setPlaceholderText("Do'kon nomini kiriting")
        self.shop_name_input.setFixedHeight(50)
        self.shop_name_input.setMaximumWidth(600)
        shop_form.addRow("Do'kon nomi:", self.shop_name_input)
        
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Do'kon manzili")
        self.address_input.setFixedHeight(50)
        self.address_input.setMaximumWidth(600)
        shop_form.addRow("Manzil:", self.address_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+998 99 123 45 67")
        self.phone_input.setFixedHeight(50)
        self.phone_input.setMaximumWidth(600)
        shop_form.addRow("Telefon:", self.phone_input)
        
        self.footer_input = QTextEdit()
        self.footer_input.setPlaceholderText("Chekda chiqadigan billing yoki minnatdorchilik matni...")
        self.footer_input.setFixedHeight(120)
        self.footer_input.setMaximumWidth(600)
        shop_form.addRow("Chek matni:", self.footer_input)
        
        shop_layout.addLayout(shop_form)
        shop_layout.addStretch()
        self.tab_widget.addTab(shop_scroll, "🏪 Do'kon")
        
        # ============================================================
        # TAB 2: FOYDALANUVCHILAR
        # ============================================================
        user_scroll, user_tab = create_scroll_tab()
        user_main_layout = QVBoxLayout(user_tab)
        user_main_layout.setContentsMargins(30, 30, 30, 30)
        user_main_layout.setSpacing(25)
        
        body_layout = QHBoxLayout()
        body_layout.setSpacing(25)
        
        left_panel = QVBoxLayout()
        left_panel.setSpacing(20)
        
        group_box_style = """
            QGroupBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 12px;
                padding-top: 35px;
                font-size: 15px;
            }
            QGroupBox::title {
                color: #6c63ff;
                font-weight: bold;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 10px 20px;
            }
            QLabel { color: #a0a0b8; font-size: 14px; }
        """
        
        # Yangi foydalanuvchi qo'shish
        add_user_group = QGroupBox("➕ Yangi foydalanuvchi qo'shish")
        add_user_group.setStyleSheet(group_box_style + input_style)
        add_user_layout = QGridLayout(add_user_group)
        add_user_layout.setSpacing(15)
        add_user_layout.setContentsMargins(20, 20, 20, 20)
        
        self.new_username = QLineEdit()
        self.new_username.setPlaceholderText("Foydalanuvchi nomi")
        self.new_username.setFixedHeight(45)
        add_user_layout.addWidget(QLabel("Username:"), 0, 0)
        add_user_layout.addWidget(self.new_username, 0, 1)
        
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Parol")
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password.setFixedHeight(45)
        add_user_layout.addWidget(QLabel("Parol:"), 1, 0)
        add_user_layout.addWidget(self.new_password, 1, 1)
        
        self.new_role = QComboBox()
        self.new_role.addItems(['cashier', 'admin'])
        self.new_role.setFixedHeight(45)
        self.new_role.setStyleSheet("""
            QComboBox {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 10px;
                padding: 8px 15px;
                color: #e0e0e0;
                font-size: 15px;
            }
            QComboBox:focus { border: 2px solid #6c63ff; }
            QComboBox::drop-down { border: none; padding-right: 10px; }
        """)
        add_user_layout.addWidget(QLabel("Roli:"), 2, 0)
        add_user_layout.addWidget(self.new_role, 2, 1)
        
        add_user_btn = QPushButton("➕ Qo'shish")
        add_user_btn.setObjectName("successButton")
        add_user_btn.setFixedHeight(45)
        add_user_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        add_user_btn.clicked.connect(self.add_user)
        add_user_layout.addWidget(add_user_btn, 3, 0, 1, 2)
        
        left_panel.addWidget(add_user_group)
        
        # Admin parolini o'zgartirish
        password_group = QGroupBox("🔑 Admin parolini o'zgartirish")
        password_group.setStyleSheet(group_box_style + input_style)
        password_layout = QGridLayout(password_group)
        password_layout.setSpacing(15)
        password_layout.setContentsMargins(20, 20, 20, 20)
        
        self.old_password_input = QLineEdit()
        self.old_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.old_password_input.setFixedHeight(45)
        password_layout.addWidget(QLabel("Eski parol:"), 0, 0)
        password_layout.addWidget(self.old_password_input, 0, 1)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setFixedHeight(45)
        password_layout.addWidget(QLabel("Yangi parol:"), 1, 0)
        password_layout.addWidget(self.new_password_input, 1, 1)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setFixedHeight(45)
        password_layout.addWidget(QLabel("Tasdiqlash:"), 2, 0)
        password_layout.addWidget(self.confirm_password_input, 2, 1)
        
        change_password_btn = QPushButton("🔑 Parolni o'zgartirish")
        change_password_btn.setObjectName("primaryButton")
        change_password_btn.setFixedHeight(45)
        change_password_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        change_password_btn.clicked.connect(self.change_admin_password)
        password_layout.addWidget(change_password_btn, 3, 0, 1, 2)
        
        left_panel.addWidget(password_group)
        body_layout.addLayout(left_panel, 4)
        
        # Foydalanuvchilar ro'yxati
        users_group = QGroupBox("👥 Foydalanuvchilar ro'yxati")
        users_group.setStyleSheet(group_box_style)
        users_layout = QVBoxLayout(users_group)
        users_layout.setContentsMargins(20, 20, 20, 20)
        users_layout.setSpacing(15)
        
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(['ID', 'Username', 'Roli', 'Yaratilgan'])
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.users_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.users_table.setStyleSheet("""
            QTableWidget {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 10px;
                gridline-color: #2a2a4a;
            }
            QHeaderView::section {
                background: #111125;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #2a2a4a;
                color: #a0a0b8;
                font-weight: bold;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QTableWidget::item:selected {
                background: #6c63ff;
                color: white;
            }
        """)
        self.users_table.verticalHeader().setDefaultSectionSize(48)
        users_layout.addWidget(self.users_table)
        
        delete_user_btn = QPushButton("🗑️ Foydalanuvchini o'chirish")
        delete_user_btn.setObjectName("dangerButton")
        delete_user_btn.setFixedHeight(45)
        delete_user_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        delete_user_btn.clicked.connect(self.delete_user)
        users_layout.addWidget(delete_user_btn)
        
        body_layout.addWidget(users_group, 6)
        user_main_layout.addLayout(body_layout)
        
        self.tab_widget.addTab(user_scroll, "👤 Foydalanuvchilar")
        
        # ============================================================
        # TAB 3: TIZIM
        # ============================================================
        system_scroll, system_tab = create_scroll_tab()
        system_layout = QVBoxLayout(system_tab)
        system_layout.setContentsMargins(40, 40, 40, 40)
        
        system_form = QFormLayout()
        system_form.setSpacing(25)
        system_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        spinbox_style = """
            QSpinBox, QDoubleSpinBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 10px;
                padding: 12px 18px;
                color: #e0e0e0;
                font-size: 15px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #6c63ff;
            }
            QLabel {
                color: #a0a0b8;
                font-size: 16px;
                font-weight: 500;
            }
        """
        system_tab.setStyleSheet(spinbox_style)
        
        self.discount_percent_input = QDoubleSpinBox()
        self.discount_percent_input.setRange(0, 100)
        self.discount_percent_input.setValue(0)
        self.discount_percent_input.setSuffix(" %")
        self.discount_percent_input.setFixedHeight(50)
        self.discount_percent_input.setFixedWidth(250)
        system_form.addRow("Chegirma foizi:", self.discount_percent_input)
        
        self.debt_days_input = QSpinBox()
        self.debt_days_input.setRange(1, 90)
        self.debt_days_input.setValue(30)
        self.debt_days_input.setSuffix(" kun")
        self.debt_days_input.setFixedHeight(50)
        self.debt_days_input.setFixedWidth(250)
        system_form.addRow("Nasiya muddati:", self.debt_days_input)
        
        self.min_stock_input = QDoubleSpinBox()
        self.min_stock_input.setRange(0, 1000)
        self.min_stock_input.setValue(5)
        self.min_stock_input.setSuffix(" dona")
        self.min_stock_input.setFixedHeight(50)
        self.min_stock_input.setFixedWidth(250)
        system_form.addRow("Kam qolgan chegarasi:", self.min_stock_input)
        
        system_layout.addLayout(system_form)
        system_layout.addStretch()
        
        self.tab_widget.addTab(system_scroll, "⚙️ Tizim")
    
    # ============================================================
    # METODLAR
    # ============================================================
    def load_settings(self):
        try:
            shop = self.shop_repo.get_settings()
            if shop:
                self.shop_name_input.setText(shop.get('shop_name', ''))
                self.address_input.setText(shop.get('address', ''))
                self.phone_input.setText(shop.get('phone', ''))
                self.footer_input.setText(shop.get('receipt_footer', ''))
            
            discount = self.setting_repo.get('discount_percent')
            if discount:
                self.discount_percent_input.setValue(float(discount))
            
            debt_days = self.setting_repo.get('debt_days')
            if debt_days:
                self.debt_days_input.setValue(int(debt_days))
            
            min_stock = self.setting_repo.get('min_stock')
            if min_stock:
                self.min_stock_input.setValue(float(min_stock))
            
            self.load_users()
        except Exception as e:
            print(f"❌ Sozlamalarni yuklashda xatolik: {e}")
    
    def load_users(self):
        try:
            users = self.user_repo.get_all_users()
            self.users_table.setRowCount(len(users))
            for i, user in enumerate(users):
                self.users_table.setItem(i, 0, QTableWidgetItem(str(user['id'])))
                self.users_table.setItem(i, 1, QTableWidgetItem(user['username']))
                self.users_table.setItem(i, 2, QTableWidgetItem(user['role']))
                self.users_table.setItem(i, 3, QTableWidgetItem(user.get('created_at', '')))
        except Exception as e:
            print(f"❌ Foydalanuvchilarni yuklashda xatolik: {e}")
    
    def save_settings(self):
        try:
            shop = self.shop_repo.get_settings()
            
            # 🔥 MUHIM: Dict shaklida yuborish
            shop_data = {
                'shop_name': self.shop_name_input.text().strip(),
                'address': self.address_input.text().strip(),
                'phone': self.phone_input.text().strip(),
                'receipt_footer': self.footer_input.toPlainText().strip()
            }
            
            if shop:
                shop_data['id'] = shop['id']
            
            # 🔥 Dict ni to'g'ri yuborish
            result = self.shop_repo.update_settings(shop_data)
            
            if result:
                self.setting_repo.set('discount_percent', str(self.discount_percent_input.value()))
                self.setting_repo.set('debt_days', str(self.debt_days_input.value()))
                self.setting_repo.set('min_stock', str(self.min_stock_input.value()))
                QMessageBox.information(self, "Muvaffaqiyat", "✅ Sozlamalar muvaffaqiyatli saqlandi!")
            else:
                QMessageBox.warning(self, "Xatolik", "Sozlamalarni saqlashda xatolik yuz berdi!")
                
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Sozlamalarni saqlashda xatolik: {str(e)}")
            print(f"❌ Save settings error: {e}")
    
    def add_user(self):
        try:
            username = self.new_username.text().strip()
            password = self.new_password.text().strip()
            role = self.new_role.currentText()
            
            if not username or not password:
                QMessageBox.warning(self, "Xatolik", "Username va parolni kiriting!")
                return
            if len(password) < 4:
                QMessageBox.warning(self, "Xatolik", "Parol kamida 4 belgidan iborat bo'lishi kerak!")
                return
            
            result = self.user_repo.create_user(username, password, role)
            if result:
                QMessageBox.information(self, "Muvaffaqiyat", f"✅ {username} foydalanuvchisi qo'shildi!")
                self.new_username.clear()
                self.new_password.clear()
                self.load_users()
            else:
                QMessageBox.warning(self, "Xatolik", "Foydalanuvchi qo'shishda xatolik! Username band bo'lishi mumkin.")
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Foydalanuvchi qo'shishda xatolik: {str(e)}")
    
    def delete_user(self):
        try:
            current_row = self.users_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Ogohlantirish", "Iltimos, o'chirish uchun foydalanuvchini tanlang!")
                return
            
            user_id = int(self.users_table.item(current_row, 0).text())
            username = self.users_table.item(current_row, 1).text()
            
            if username == 'admin':
                QMessageBox.warning(self, "Xatolik", "Admin foydalanuvchisini o'chirib bo'lmaydi!")
                return
            
            reply = QMessageBox.question(
                self, "Tasdiqlash", f"'{username}' foydalanuvchisini o'chirmoqchimisiz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                result = api.delete(f"/auth/users/{user_id}")

                if result:
                    QMessageBox.information(self, "Muvaffaqiyat", "✅ Foydalanuvchi o'chirildi!")
                    self.load_users()
                else:
                    QMessageBox.warning(self, "Xatolik", "Foydalanuvchini o'chirishda xatolik!")
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Foydalanuvchini o'chirishda xatolik: {str(e)}")
    
    def change_admin_password(self):
        try:
            old_password = self.old_password_input.text().strip()
            new_password = self.new_password_input.text().strip()
            confirm_password = self.confirm_password_input.text().strip()
            
            if not old_password or not new_password or not confirm_password:
                QMessageBox.warning(self, "Xatolik", "Iltimos, barcha maydonlarni to'ldiring!")
                return
            if len(new_password) < 4:
                QMessageBox.warning(self, "Xatolik", "Yangi parol kamida 4 belgidan iborat bo'lishi kerak!")
                return
            if new_password != confirm_password:
                QMessageBox.warning(self, "Xatolik", "Yangi parol va tasdiqlash mos kelmadi!")
                return
            
            admin_user = {"username": "admin", "password_hash": ""}  # Check via API
            if not admin_user:
                QMessageBox.warning(self, "Xatolik", "Admin foydalanuvchisi topilmadi!")
                return
            
            stored_hash = admin_user['password_hash']
            if not bcrypt.checkpw(old_password.encode('utf-8'), stored_hash.encode('utf-8')):
                QMessageBox.warning(self, "Xatolik", "Eski parol noto'g'ri!")
                return
            
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            # Password is updated via API
            from models.api_client import api as _api
            result = _api.put("/settings/admin-password", {"old_password": old_password, "new_password": new_password})
            
            if result > 0:
                QMessageBox.information(self, "Muvaffaqiyat", "✅ Admin paroli muvaffaqiyatli o'zgartirildi!")
                self.old_password_input.clear()
                self.new_password_input.clear()
                self.confirm_password_input.clear()
            else:
                QMessageBox.warning(self, "Xatolik", "Parolni o'zgartirishda xatolik yuz berdi!")
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Parolni o'zgartirishda xatolik: {str(e)}")