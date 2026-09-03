# # views/sms_view.py
# from PyQt6.QtWidgets import *
# from PyQt6.QtCore import *
# from PyQt6.QtGui import *
# from utils.styles import DARK_STYLE
# from controllers.sale_controller import SaleController
# from datetime import datetime, timedelta

# class SMSView(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.sale_controller = SaleController()
#         self.selected_customer = None
#         self.setup_ui()
#         self.setStyleSheet(DARK_STYLE)
#         self.load_customers()
        
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.load_customers)
#         self.timer.start(30000)
    
#     def setup_ui(self):
#         layout = QVBoxLayout(self)
#         layout.setSpacing(15)
#         layout.setContentsMargins(20, 20, 20, 20)
        
#         # Header
#         header_widget = QWidget()
#         header_widget.setStyleSheet("""
#             QWidget {
#                 background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
#                     stop: 0 #1a1a2e, stop: 1 #2a2a4a);
#                 border-radius: 15px;
#                 padding: 20px;
#             }
#         """)
#         header_layout = QHBoxLayout(header_widget)
        
#         title = QLabel("📱 SMS xabarnoma")
#         title.setObjectName("titleLabel")
#         title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
#         header_layout.addWidget(title)
        
#         header_layout.addStretch()
        
#         refresh_btn = QPushButton("🔄 Yangilash")
#         refresh_btn.setObjectName("primaryButton")
#         refresh_btn.clicked.connect(self.load_customers)
#         header_layout.addWidget(refresh_btn)
        
#         layout.addWidget(header_widget)
        
#         # Statistika
#         stats_layout = QHBoxLayout()
#         self.stats_labels = {}
#         stats = [
#             ("📋 Navbatdagi mijozlar", "count", "0"),
#             ("📱 Telefon raqami bor", "sent", "0"),
#             ("⏳ Telefon raqami yo'q", "pending", "0")
#         ]
        
#         for label, key, default in stats:
#             group = QGroupBox(label)
#             group.setStyleSheet("""
#                 QGroupBox {
#                     background: #1a1a2e;
#                     border: 2px solid #2a2a4a;
#                     border-radius: 12px;
#                     padding: 10px;
#                 }
#                 QGroupBox::title {
#                     color: #a0a0b8;
#                     font-weight: bold;
#                     padding: 0 10px;
#                 }
#             """)
#             group_layout = QVBoxLayout(group)
#             label_widget = QLabel(default)
#             label_widget.setObjectName("cardValue")
#             label_widget.setStyleSheet("font-size: 24px; color: #6c63ff; font-weight: bold;")
#             group_layout.addWidget(label_widget)
#             stats_layout.addWidget(group)
#             self.stats_labels[key] = label_widget
        
#         layout.addLayout(stats_layout)
        
#         # Splitter
#         splitter = QSplitter(Qt.Orientation.Horizontal)
#         splitter.setStyleSheet("""
#             QSplitter::handle {
#                 background: #2a2a4a;
#                 width: 2px;
#             }
#         """)
        
#         # ===== LEFT PANEL - CUSTOMERS =====
#         left_widget = QWidget()
#         left_layout = QVBoxLayout(left_widget)
#         left_layout.setContentsMargins(0, 0, 0, 0)
        
#         customer_label = QLabel("📋 Navbatdagi mijozlar (ustiga bosing)")
#         customer_label.setStyleSheet("color: #a0a0b8; font-weight: bold; font-size: 14px; padding: 5px;")
#         left_layout.addWidget(customer_label)
        
#         self.customer_table = QTableWidget()
#         self.customer_table.setColumnCount(5)
#         self.customer_table.setHorizontalHeaderLabels([
#             'ID', 'Mashina', 'Telefon', 'Keyingi sana', 'Holat'
#         ])
#         self.customer_table.setStyleSheet("""
#             QTableWidget {
#                 background: #1a1a2e;
#                 border: 2px solid #2a2a4a;
#                 border-radius: 10px;
#             }
#             QHeaderView::section {
#                 background: #1a1a32;
#                 padding: 10px;
#                 border: none;
#                 border-bottom: 2px solid #2a2a4a;
#                 color: #a0a0b8;
#                 font-weight: bold;
#             }
#             QTableWidget::item {
#                 padding: 8px;
#                 color: #e0e0e0;
#             }
#             QTableWidget::item:selected {
#                 background: #4a4a8a;
#                 color: white;
#             }
#         """)
#         self.customer_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
#         self.customer_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
#         self.customer_table.itemClicked.connect(self.on_customer_selected)
#         left_layout.addWidget(self.customer_table)
        
#         splitter.addWidget(left_widget)
        
#         # ===== RIGHT PANEL - SMS MESSAGE =====
#         right_widget = QWidget()
#         right_widget.setFixedWidth(500)
#         right_layout = QVBoxLayout(right_widget)
#         right_layout.setContentsMargins(0, 0, 0, 0)
        
#         # Tanlangan mijoz haqida ma'lumot
#         self.selected_info = QLabel("👤 Tanlangan mijoz: Yo'q")
#         self.selected_info.setStyleSheet("""
#             color: #a0a0b8; 
#             font-size: 14px; 
#             padding: 10px; 
#             background: #1a1a2e; 
#             border-radius: 8px;
#             border: 1px solid #2a2a4a;
#         """)
#         right_layout.addWidget(self.selected_info)
        
#         template_label = QLabel("📝 Tayyor SMS matni (mijoz ma'lumotlari bilan to'ldiriladi)")
#         template_label.setStyleSheet("color: #a0a0b8; font-weight: bold; font-size: 13px; padding: 5px;")
#         right_layout.addWidget(template_label)
        
#         self.template_combo = QComboBox()
#         self.template_combo.addItems([
#             "📌 Standart eslatma (3 kun)",
#             "📌 Ertaga kelish eslatmasi",
#             "🔴 Bugun kelish eslatmasi",
#             "✅ Xizmatdan keyin minnatdorchilik"
#         ])
#         self.template_combo.setStyleSheet("""
#             QComboBox {
#                 background: #1a1a2e;
#                 border: 2px solid #2a2a4a;
#                 border-radius: 8px;
#                 padding: 8px 12px;
#                 color: #e0e0e0;
#                 font-size: 14px;
#             }
#             QComboBox::drop-down {
#                 border: none;
#             }
#         """)
#         self.template_combo.currentIndexChanged.connect(self.generate_sms)
#         right_layout.addWidget(self.template_combo)
        
#         # SMS matni (to'ldirilgan holda)
#         self.sms_text = QTextEdit()
#         self.sms_text.setPlaceholderText("Mijoz tanlang, SMS matni avtomatik to'ldiriladi...")
#         self.sms_text.setStyleSheet("""
#             QTextEdit {
#                 background: #1a1a2e;
#                 border: 2px solid #2a2a4a;
#                 border-radius: 10px;
#                 padding: 15px;
#                 color: #e0e0e0;
#                 font-size: 14px;
#                 min-height: 300px;
#                 font-family: 'Courier New';
#             }
#             QTextEdit:focus {
#                 border: 2px solid #6c63ff;
#             }
#         """)
#         right_layout.addWidget(self.sms_text)
        
#         # Buttons
#         btn_layout = QHBoxLayout()
        
#         copy_btn = QPushButton("📋 Matnni nusxalash")
#         copy_btn.setObjectName("primaryButton")
#         copy_btn.setMinimumHeight(40)
#         copy_btn.clicked.connect(self.copy_text)
#         btn_layout.addWidget(copy_btn)
        
#         clear_btn = QPushButton("🗑️ Tozalash")
#         clear_btn.setObjectName("dangerButton")
#         clear_btn.setMinimumHeight(40)
#         clear_btn.clicked.connect(self.clear_text)
#         btn_layout.addWidget(clear_btn)
        
#         right_layout.addLayout(btn_layout)
        
#         # Eslatma
#         note = QLabel("💡 Mijozni tanlang, SMS matni avtomatik to'ldiriladi. Keyin Copy qilib o'zingiz yuboring.")
#         note.setStyleSheet("color: #a0a0b8; font-size: 12px; padding: 8px; background: #1a1a2e; border-radius: 8px;")
#         note.setWordWrap(True)
#         right_layout.addWidget(note)
        
#         splitter.addWidget(right_widget)
#         splitter.setSizes([450, 500])
        
#         layout.addWidget(splitter)
    
#     def load_customers(self):
#         try:
#             customers = self.sale_controller.get_upcoming_notifications(3)
            
#             self.customer_table.setRowCount(len(customers))
            
#             has_phone = 0
#             no_phone = 0
            
#             for i, c in enumerate(customers):
#                 self.customer_table.setItem(i, 0, QTableWidgetItem(str(c.get('id', ''))))
#                 self.customer_table.setItem(i, 1, QTableWidgetItem(c.get('car_number', '-')))
#                 self.customer_table.setItem(i, 2, QTableWidgetItem(c.get('phone_number', '-')))
#                 self.customer_table.setItem(i, 3, QTableWidgetItem(c.get('next_oil_change_date', '-')))
                
#                 today = datetime.now().date().strftime("%Y-%m-%d")
#                 if c.get('next_oil_change_date') == today:
#                     status = "🔴 Bugun"
#                 else:
#                     status = "🟡 Kutilmoqda"
                
#                 self.customer_table.setItem(i, 4, QTableWidgetItem(status))
                
#                 if c.get('phone_number') and c.get('phone_number') != '-':
#                     has_phone += 1
#                 else:
#                     no_phone += 1
            
#             self.stats_labels['count'].setText(str(len(customers)))
#             self.stats_labels['sent'].setText(str(has_phone))
#             self.stats_labels['pending'].setText(str(no_phone))
            
#             self.customer_table.resizeColumnsToContents()
            
#         except Exception as e:
#             print(f"Error loading customers: {e}")
    
#     def on_customer_selected(self, item):
#         """Mijoz tanlanganda SMS matnini to'ldirish"""
#         try:
#             row = item.row()
#             customer_id = int(self.customer_table.item(row, 0).text())
            
#             # Mijoz ma'lumotlarini olish
#             customers = self.sale_controller.get_upcoming_notifications(3)
#             self.selected_customer = None
#             for c in customers:
#                 if c.get('id') == customer_id:
#                     self.selected_customer = c
#                     break
            
#             if self.selected_customer:
#                 car_number = self.selected_customer.get('car_number', '-')
#                 phone = self.selected_customer.get('phone_number', '-')
#                 next_date = self.selected_customer.get('next_oil_change_date', '-')
                
#                 self.selected_info.setText(
#                     f"👤 Mijoz: 🚗 {car_number} | 📱 {phone} | 📅 {next_date}"
#                 )
                
#                 # SMS matnini yaratish
#                 self.generate_sms()
                
#         except Exception as e:
#             print(f"Error selecting customer: {e}")
    
# # views/sms_view.py - generate_sms metodidagi templates ni yangilang

# def generate_sms(self):
#     if not self.selected_customer:
#         self.sms_text.setText("Iltimos, chap tomondan mijozni tanlang!")
#         return
    
#     index = self.template_combo.currentIndex()
    
#     car_number = self.selected_customer.get('car_number', '-')
#     phone = self.selected_customer.get('phone_number', '-')
#     next_date = self.selected_customer.get('next_oil_change_date', '-')
    
#     templates = [
#         # ===== 1. STANDART ESLATMA (3 kun) =====
#         f"""🏪 POS Tizimi

# Hurmatli {car_number} raqamli mashina egasi!

# Sizni {next_date} kuni xizmat ko'rsatish markaziga taklif qilamiz.

# 🔧 Sababi: Mashinangizda moy almashtirish vaqti kelgan!

# 📍 Manzil: Qo'qon Shaxar Benazir Kafe ro'pparasida
# 📞 Telefon: +998 88 969 05 05

# ⏰ Ish vaqti: 09:00 - 20:00

# Rahmat!

# 📱 Bizni ijtimoiy tarmoqlarda kuzating:
# 📷 Instagram: https://www.instagram.com/avtomoychi
# ▶️ YouTube: https://www.youtube.com/@Avtomoychi
# 💬 Telegram: @avtomoychi""",

#         # ===== 2. ERTAGA KELISH ESLATMASI =====
#         f"""🏪 POS Tizimi

# ⚠️ Eslatma!

# Hurmatli {car_number} raqamli mashina egasi!

# Sizni ertaga ({next_date}) xizmat ko'rsatish markaziga taklif qilamiz.

# 🔧 Mashinangizda moy almashtirish vaqti kelgan!

# 📍 Manzil: Qo'qon Shaxar Benazir Kafe ro'pparasida
# 📞 Telefon: +998 88 969 05 05

# ⏰ Ish vaqti: 09:00 - 20:00

# Iltimos, kelishni unutmang!

# 📱 Bizni ijtimoiy tarmoqlarda kuzating:
# 📷 Instagram: https://www.instagram.com/avtomoychi
# ▶️ YouTube: https://www.youtube.com/@Avtomoychi
# 💬 Telegram: @avtomoychi""",

#         # ===== 3. BUGUN KELISH ESLATMASI =====
#         f"""🏪 POS Tizimi

# 🔴 DIQQAT!

# Hurmatli {car_number} raqamli mashina egasi!

# Sizni BUGUN ({next_date}) xizmat ko'rsatish markaziga taklif qilamiz.

# ⚠️ Mashinangizda moy almashtirish vaqti kelgan!

# 📍 Manzil: Qo'qon Shaxar Benazir Kafe ro'pparasida
# 📞 Telefon: +998 88 969 05 05

# ⏰ Ish vaqti: 09:00 - 20:00

# Bugun kelishingizni unutmang!

# 📱 Bizni ijtimoiy tarmoqlarda kuzating:
# 📷 Instagram: https://www.instagram.com/avtomoychi
# ▶️ YouTube: https://www.youtube.com/@Avtomoychi
# 💬 Telegram: @avtomoychi""",

#         # ===== 4. XIZMATDAN KEYIN MINNATDORCHILIK =====
#         f"""🏪 POS Tizimi

# ✅ Xizmatdan keyin minnatdorchilik!

# Hurmatli {car_number} raqamli mashina egasi!

# Sizning mashinangizga moy almashtirish xizmati muvaffaqiyatli amalga oshirildi.

# 📅 Xizmat sanasi: {next_date}

# 🛢️ Moy turi: ...
# 📏 Kilometraj: ... km

# Keyingi moy almashtirish: 6 oydan keyin yoki 5000 km dan keyin.

# Bizni tanlaganingiz uchun rahmat! Xush kelibsiz!

# 📍 Manzil: Qo'qon Shaxar Benazir Kafe ro'pparasida
# 📞 Telefon: +998 88 969 05 05

# 📱 Bizni ijtimoiy tarmoqlarda kuzating:
# 📷 Instagram: https://www.instagram.com/avtomoychi
# ▶️ YouTube: https://www.youtube.com/@Avtomoychi
# 💬 Telegram: @avtomoychi"""
#     ]
    
#     if index < len(templates):
#         self.sms_text.setText(templates[index])
        
#         """Tanlangan mijoz va template bo'yicha SMS matnini yaratish"""
#         if not self.selected_customer:
#             self.sms_text.setText("👈 Iltimos, chap tomondan mijozni tanlang!")
#             return
        
#         index = self.template_combo.currentIndex()
        
#         car_number = self.selected_customer.get('car_number', '-')
#         phone = self.selected_customer.get('phone_number', '-')
#         next_date = self.selected_customer.get('next_oil_change_date', '-')
        
#         templates = [
#             # ===== 1. STANDART ESLATMA =====
#             f"""🏪 POS Tizimi

# Hurmatli {car_number} raqamli mashina egasi!

# Sizni {next_date} kuni xizmat ko'rsatish markaziga taklif qilamiz.

# 🔧 Sababi: Mashinangizda moy almashtirish vaqti kelgan!

# 📍 Manzil: Toshkent sh., ... ko'chasi, ...-uy
# 📞 Telefon: +998 99 123 45 67

# ⏰ Ish vaqti: Dushanba-Shanba 09:00 - 20:00

# Rahmat!

# 📱 Bizni ijtimoiy tarmoqlarda kuzating:
# 📷 Instagram: @pos_tizimi
# ▶️ YouTube: POS Tizimi
# 💬 Telegram: @pos_tizimi""",

#             # ===== 2. ERTAGA KELISH ESLATMASI =====
#             f"""🏪 POS Tizimi

# ⚠️ Eslatma!

# Hurmatli {car_number} raqamli mashina egasi!

# Sizni ertaga ({next_date}) xizmat ko'rsatish markaziga taklif qilamiz.

# 🔧 Mashinangizda moy almashtirish vaqti kelgan!

# 📍 Manzil: Toshkent sh., ... ko'chasi, ...-uy
# 📞 Telefon: +998 99 123 45 67

# Iltimos, kelishni unutmang!

# 📱 Bizni ijtimoiy tarmoqlarda kuzating:
# 📷 Instagram: @pos_tizimi
# ▶️ YouTube: POS Tizimi
# 💬 Telegram: @pos_tizimi""",

#             # ===== 3. BUGUN KELISH ESLATMASI =====
#             f"""🏪 POS Tizimi

# 🔴 DIQQAT!

# Hurmatli {car_number} raqamli mashina egasi!

# Sizni BUGUN ({next_date}) xizmat ko'rsatish markaziga taklif qilamiz.

# ⚠️ Mashinangizda moy almashtirish vaqti kelgan!

#     📍 Manzil: Qo'qon Shaxar Benazir Kafe ro'pparasida 
#     📞 Telefon: +998 88 969 05 05

#     ⏰ Ish vaqti: 09:00 - 20:00

#     Bugun kelishingizni unutmang!

#     📱 Bizni ijtimoiy tarmoqlarda kuzating:
#     📷 Instagram: https://www.instagram.com/avtomoychi
#     ▶️ YouTube: https://www.youtube.com/@Avtomoychi
#     💬 Telegram: @avtomoychi,

#             # ===== 4. XIZMATDAN KEYIN MINNATDORCHILIK =====
#             f"""🏪 POS Tizimi

# ✅ Xizmatdan keyin minnatdorchilik!

# Hurmatli {car_number} raqamli mashina egasi!

# Sizning mashinangizga moy almashtirish xizmati muvaffaqiyatli amalga oshirildi.

# 📅 Xizmat sanasi: {next_date}

# Keyingi moy almashtirish: 6 oydan keyin yoki 5000 km dan keyin.

# Bizni tanlaganingiz uchun rahmat! Xush kelibsiz!

# 📱 Bizni ijtimoiy tarmoqlarda kuzating:
# 📷 Instagram: @pos_tizimi
# ▶️ YouTube: POS Tizimi
# 💬 Telegram: @pos_tizimi"""
#         ]
        
#         if index < len(templates):
#             self.sms_text.setText(templates[index])
    
#     def copy_text(self):
#         """Matnni nusxalash"""
#         text = self.sms_text.toPlainText()
#         if text and not text.startswith("👈"):
#             clipboard = QApplication.clipboard()
#             clipboard.setText(text)
#             QMessageBox.information(self, "Muvaffaqiyat", "✅ SMS matni nusxalandi!\n\nEndi telefoningizdan mijozga yuboring.")
#         else:
#             QMessageBox.warning(self, "Xatolik", "❌ Iltimos, avval mijozni tanlang!")
    
#     def clear_text(self):
#         """Matnni tozalash"""
#         self.sms_text.clear()
#         self.selected_customer = None
#         self.selected_info.setText("👤 Tanlangan mijoz: Yo'q")
#         self.sms_text.setPlaceholderText("👈 Iltimos, chap tomondan mijozni tanlang!")



# views/sms_view.py - TO'LIQ TUZATILGAN

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils.styles import DARK_STYLE
from controllers.sale_controller import SaleController
from datetime import datetime, timedelta

class SMSView(QWidget):
    def __init__(self):
        super().__init__()
        self.sale_controller = SaleController()
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.load_customers()
    
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
        
        title = QLabel("📱 SMS xabarnoma")
        title.setObjectName("titleLabel")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Yangilash")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.clicked.connect(self.load_customers)
        header_layout.addWidget(refresh_btn)
        
        layout.addWidget(header_widget)
        
        # Stats
        stats_layout = QHBoxLayout()
        self.stats_labels = {}
        stats = [
            ("📋 Navbatdagi mijozlar", "count", "0", "#6c63ff"),
            ("📱 Telefon raqami bor", "has_phone", "0", "#00c853"),
            ("❌ Telefon raqami yoq", "no_phone", "0", "#ff5252")
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
            label_widget.setStyleSheet(f"font-size: 28px; color: {color}; font-weight: bold;")
            label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            group_layout.addWidget(label_widget)
            stats_layout.addWidget(group)
            self.stats_labels[key] = label_widget
        
        layout.addLayout(stats_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Mashina', 'Telefon', 'Keyingi sana', 'Holat'
        ])
        self.table.setStyleSheet("""
            QTableWidget {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 10px;
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
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        
        # Ustun kengliklari
        self.table.setColumnWidth(0, 50)   # ID
        self.table.setColumnWidth(1, 150)  # Mashina
        self.table.setColumnWidth(2, 150)  # Telefon
        self.table.setColumnWidth(3, 120)  # Keyingi sana
        self.table.setColumnWidth(4, 100)  # Holat
        
        layout.addWidget(self.table)
        
        # SMS yozish
        sms_group = QGroupBox("✉️ SMS yozish")
        sms_group.setStyleSheet("""
            QGroupBox {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 12px;
                padding: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                color: #a0a0b8;
                font-weight: bold;
                padding: 0 10px;
            }
        """)
        
        sms_layout = QVBoxLayout(sms_group)
        sms_layout.setSpacing(10)
        
        # Tanlangan mijoz
        selected_layout = QHBoxLayout()
        selected_layout.addWidget(QLabel("📌 Tanlangan mijoz:"))
        self.selected_label = QLabel("Yo'q")
        self.selected_label.setStyleSheet("color: #6c63ff; font-weight: bold;")
        selected_layout.addWidget(self.selected_label)
        selected_layout.addStretch()
        sms_layout.addLayout(selected_layout)
        
        # SMS matni
        sms_layout.addWidget(QLabel("📝 Tayyor SMS matni (mijoz ma'lumotlari bilan to'ldiriladi):"))
        
        self.sms_text = QTextEdit()
        self.sms_text.setPlaceholderText("Mijoz tanlang, SMS matni avtomatik to'ldiriladi...")
        self.sms_text.setMaximumHeight(120)
        self.sms_text.setStyleSheet("""
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
        sms_layout.addWidget(self.sms_text)
        
        # Tugmalar
        sms_button_layout = QHBoxLayout()
        sms_button_layout.setSpacing(10)
        
        copy_btn = QPushButton("📋 Matnni nusxalash")
        copy_btn.setObjectName("primaryButton")
        copy_btn.setMinimumHeight(40)
        copy_btn.clicked.connect(self.copy_sms_text)
        sms_button_layout.addWidget(copy_btn)
        
        clear_btn = QPushButton("🗑️ Tozalash")
        clear_btn.setObjectName("dangerButton")
        clear_btn.setMinimumHeight(40)
        clear_btn.clicked.connect(self.clear_sms)
        sms_button_layout.addWidget(clear_btn)
        
        sms_layout.addLayout(sms_button_layout)
        
        layout.addWidget(sms_group)
        
        # Eslatma
        note = QLabel("💡 Eslatma: Mijozni tanlang, SMS matni avtomatik to'ldiriladi. Keyin Copy qilib o'zingiz yuboring.")
        note.setStyleSheet("color: #a0a0b8; font-size: 13px; padding: 10px; background: #1a1a2e; border-radius: 8px;")
        note.setWordWrap(True)
        layout.addWidget(note)
    
    def load_customers(self):
        """Navbatdagi mijozlarni yuklash"""
        try:
            # 🔥 MUHIM: Controllerni yangilash
            self.sale_controller = SaleController()
            
            # 3 kun ichida keladigan mijozlar
            notifications = self.sale_controller.get_upcoming_notifications(3)
            
            # Statistikani hisoblash
            has_phone = 0
            no_phone = 0
            
            self.table.setRowCount(0)
            
            if not notifications:
                self.stats_labels['count'].setText("0")
                self.stats_labels['has_phone'].setText("0")
                self.stats_labels['no_phone'].setText("0")
                
                self.table.setRowCount(1)
                empty_item = QTableWidgetItem("📭 Navbatdagi mijozlar yo'q")
                empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                empty_item.setForeground(QColor(160, 160, 184))
                self.table.setItem(0, 0, empty_item)
                self.table.setSpan(0, 0, 1, 5)
                self.table.setRowHeight(0, 50)
                return
            
            # 🔥 MUHIM: notifications - bu Sale obyektlari ro'yxati
            self.table.setRowCount(len(notifications))
            
            for i, sale in enumerate(notifications):
                # ID
                id_item = QTableWidgetItem(str(sale.id if hasattr(sale, 'id') else ''))
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, 0, id_item)
                
                # Mashina raqami
                car_number = sale.car_number if hasattr(sale, 'car_number') else '-'
                self.table.setItem(i, 1, QTableWidgetItem(car_number))
                
                # Telefon
                phone = sale.phone_number if hasattr(sale, 'phone_number') else ''
                phone_item = QTableWidgetItem(phone if phone else '-')
                if phone:
                    has_phone += 1
                    phone_item.setForeground(QColor(0, 200, 0))
                else:
                    no_phone += 1
                    phone_item.setForeground(QColor(255, 82, 82))
                self.table.setItem(i, 2, phone_item)
                
                # Keyingi sana
                next_oil_date = sale.next_oil_change_date if hasattr(sale, 'next_oil_change_date') else '-'
                self.table.setItem(i, 3, QTableWidgetItem(next_oil_date))
                
                # Holat
                if phone:
                    status = "✅ Telefon bor"
                    status_color = QColor(0, 200, 0)
                else:
                    status = "❌ Telefon yo'q"
                    status_color = QColor(255, 82, 82)
                
                status_item = QTableWidgetItem(status)
                status_item.setForeground(status_color)
                self.table.setItem(i, 4, status_item)
            
            # Statistikani yangilash
            self.stats_labels['count'].setText(str(len(notifications)))
            self.stats_labels['has_phone'].setText(str(has_phone))
            self.stats_labels['no_phone'].setText(str(no_phone))
            
            self.table.resizeColumnsToContents()
            print(f"✅ {len(notifications)} ta mijoz yuklandi (Telefon bor: {has_phone}, Yo'q: {no_phone})")
            
            # Table selection changed
            self.table.itemSelectionChanged.connect(self.on_customer_selected)
            
        except Exception as e:
            print(f"❌ Error loading customers: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Xatolik", f"Mijozlarni yuklashda xatolik: {str(e)}")
    
    def on_customer_selected(self):
        """Mijoz tanlanganda SMS matnini tayyorlash"""
        try:
            current_row = self.table.currentRow()
            if current_row < 0:
                self.selected_label.setText("Yo'q")
                self.sms_text.clear()
                self.sms_text.setPlaceholderText("Mijoz tanlang, SMS matni avtomatik to'ldiriladi...")
                return
            
            # Ma'lumotlarni olish
            car_number_item = self.table.item(current_row, 1)
            phone_item = self.table.item(current_row, 2)
            next_date_item = self.table.item(current_row, 3)
            
            if not car_number_item or not phone_item:
                return
            
            car_number = car_number_item.text()
            phone = phone_item.text()
            next_date = next_date_item.text() if next_date_item else ""
            
            # Tanlangan mijozni ko'rsatish
            self.selected_label.setText(f"🚗 {car_number} ({phone})")
            
            # SMS matnini tayyorlash
            if phone and phone != '-':
                sms_text = f"""Assalomu alaykum!

🚗 Mashina: {car_number}
📅 Moy almashtirish vaqti kelgan:
   {next_date}

Iltimos, tezroq kelib, moy almashtiring!

🏪 Moy almashtirish
📞 +998 99 123 45 67"""
                self.sms_text.setText(sms_text)
            else:
                self.sms_text.setText(f"❌ Bu mijozning telefon raqami mavjud emas!\n\nMashina: {car_number}\nKeyingi sana: {next_date}")
                self.sms_text.setStyleSheet("""
                    QTextEdit {
                        background: #1a0a0a;
                        border: 2px solid #ff5252;
                        border-radius: 8px;
                        padding: 10px 15px;
                        color: #ff5252;
                        font-size: 14px;
                    }
                """)
                return
            
            self.sms_text.setStyleSheet("""
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
            
        except Exception as e:
            print(f"❌ Error selecting customer: {e}")
    
    def copy_sms_text(self):
        """SMS matnini nusxalash"""
        try:
            text = self.sms_text.toPlainText()
            if not text:
                QMessageBox.warning(self, "Ogohlantirish", "SMS matni bo'sh!")
                return
            
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            QMessageBox.information(self, "Muvaffaqiyat", "✅ SMS matni nusxalandi!")
            
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Nusxalashda xatolik: {str(e)}")
    
    def clear_sms(self):
        """SMS matnini tozalash"""
        self.sms_text.clear()
        self.sms_text.setPlaceholderText("Mijoz tanlang, SMS matni avtomatik to'ldiriladi...")
        self.selected_label.setText("Yo'q")
        self.table.clearSelection()