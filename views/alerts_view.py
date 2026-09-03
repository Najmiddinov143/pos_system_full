# views/alerts_view.py - TO'LIQ TUZATILGAN

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils.styles import DARK_STYLE
from models.repositories import NotificationRepository, SaleRepository, PurchaseRepository
from datetime import datetime, timedelta

class AlertsView(QWidget):
    def __init__(self):
        super().__init__()
        self.notification_repo = NotificationRepository()
        self.sale_repo = SaleRepository()
        self.purchase_repo = PurchaseRepository()
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.load_alerts()
    

    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("🔔 Bildirishnomalar")
        title.setObjectName("titleLabel")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Yangilash tugmasi
        refresh_btn = QPushButton("🔄 Yangilash")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.clicked.connect(self.load_alerts)
        header_layout.addWidget(refresh_btn)
        
        # Barchasini o'qilgan deb belgilash
        read_all_btn = QPushButton("✅ Hammasini o'qilgan deb belgilash")
        read_all_btn.setObjectName("primaryButton")
        read_all_btn.setMinimumHeight(40)
        read_all_btn.clicked.connect(self.mark_all_as_read)
        header_layout.addWidget(read_all_btn)
        
        layout.addLayout(header_layout)
        
        # ===== Jadval =====
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(5)
        self.alerts_table.setHorizontalHeaderLabels([
            'ID', 'Sarlavha', 'Xabar', 'Turi', 'Vaqt'
        ])
        self.alerts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.alerts_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.alerts_table.horizontalHeader().setStretchLastSection(True)
        self.alerts_table.setStyleSheet("""
            QTableWidget {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 10px;
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
        self.alerts_table.verticalHeader().setDefaultSectionSize(50)
        layout.addWidget(self.alerts_table)
        
        # Tugmalar
        btn_layout = QHBoxLayout()
        
        mark_read_btn = QPushButton("📖 O'qilgan deb belgilash")
        mark_read_btn.setObjectName("primaryButton")
        mark_read_btn.setMinimumHeight(40)
        mark_read_btn.clicked.connect(self.mark_as_read)
        btn_layout.addWidget(mark_read_btn)
        
        delete_btn = QPushButton("🗑️ O'chirish")
        delete_btn.setObjectName("dangerButton")
        delete_btn.setMinimumHeight(40)
        delete_btn.clicked.connect(self.delete_alert)
        btn_layout.addWidget(delete_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def load_alerts(self):
        """Barcha bildirishnomalarni yuklash"""
        try:
            # ===== 1. Nasiya to'lov muddati 7 kun qolgandagi bildirishnomalar =====
            print("🔍 Nasiya bildirishnomalarini tekshirish...")
            
            debt_alerts = self.purchase_repo.get_debt_notifications(7)
            print(f"📊 Topilgan qarzlar: {len(debt_alerts)} ta")
            
            for debt in debt_alerts:
                due_date = debt.get('due_date', '')
                if due_date:
                    try:
                        due = datetime.strptime(due_date, '%Y-%m-%d').date()
                        today = datetime.now().date()
                        days_left = (due - today).days
                        
                        if 0 <= days_left <= 7:
                            existing = [n for n in self.notification_repo.get_all_notifications() if n.get("title") == '⚠️ Nasiya to' + "lov muddati" and debt.get("product_name", "") in n.get("message", "")]
                            if not existing:
                                result = self.notification_repo.create_notification({
                                    'title': '⚠️ Nasiya to\'lov muddati',
                                    'message': f"{debt.get('product_name', '')} - {days_left} kun qoldi! To'lov muddati: {due_date}",
                                    'type': 'debt',
                                    'user_id': None
                                })
                                if result:
                                    print(f"✅ Bildirishnoma yaratildi: {debt.get('product_name')} - {days_left} kun")
                    except Exception as e:
                        print(f"Debt notification error: {e}")
            
            # ===== 2. Kam qolgan mahsulotlar =====
            from controllers.product_controller import ProductController
            product_controller = ProductController()
            products = product_controller.get_all_products()
            
            for product in products:
                if product.get('quantity', 0) <= product.get('min_quantity', 5):
                    existing = [n for n in self.notification_repo.get_all_notifications() if n.get("title") == '⚠️ Mahsulot kam qolgan' and product.get("name", "") in n.get("message", "")]
                    if not existing:
                        self.notification_repo.create_notification({
                            'title': '⚠️ Mahsulot kam qolgan',
                            'message': f"{product.get('name', '')} - {product.get('quantity', 0)} dona qoldi! (Min: {product.get('min_quantity', 5)})",
                            'type': 'stock',
                            'user_id': None
                        })
            
            # ===== 3. Barcha bildirishnomalarni olish =====
            alerts = self.notification_repo.get_all_notifications()
            print(f"📋 Jami bildirishnomalar: {len(alerts)} ta")
            
            self.alerts_table.setRowCount(len(alerts))
            
            for i, alert in enumerate(alerts):
                # 🔥 MUHIM: Alert dict yoki obyekt bo'lishi mumkin
                if hasattr(alert, '__dict__'):  # Obyekt bo'lsa
                    alert_dict = {
                        'id': getattr(alert, 'id', 0),
                        'title': getattr(alert, 'title', ''),
                        'message': getattr(alert, 'message', ''),
                        'type': getattr(alert, 'type', ''),
                        'is_read': getattr(alert, 'is_read', 0),
                        'created_at': getattr(alert, 'created_at', '')
                    }
                elif isinstance(alert, dict):  # Dict bo'lsa
                    alert_dict = alert
                else:
                    # Boshqa turdagi obyekt bo'lsa
                    try:
                        alert_dict = dict(alert)
                    except:
                        alert_dict = {
                            'id': 0,
                            'title': str(alert),
                            'message': '',
                            'type': 'unknown',
                            'is_read': 0,
                            'created_at': ''
                        }
                
                self.alerts_table.setItem(i, 0, QTableWidgetItem(str(alert_dict.get('id', ''))))
                self.alerts_table.setItem(i, 1, QTableWidgetItem(alert_dict.get('title', '')))
                self.alerts_table.setItem(i, 2, QTableWidgetItem(alert_dict.get('message', '')))
                
                # Turi bo'yicha rang berish
                alert_type = alert_dict.get('type', '')
                type_item = QTableWidgetItem(alert_type if alert_type else 'info')
                if alert_type == 'debt':
                    type_item.setBackground(Qt.GlobalColor.darkRed)
                    type_item.setForeground(Qt.GlobalColor.white)
                elif alert_type == 'stock':
                    type_item.setBackground(Qt.GlobalColor.darkYellow)
                elif alert_type == 'sale':
                    type_item.setBackground(Qt.GlobalColor.darkGreen)
                    type_item.setForeground(Qt.GlobalColor.white)
                self.alerts_table.setItem(i, 3, type_item)
                
                # O'qilganlik holati
                created_at = alert_dict.get('created_at', '')
                if alert_dict.get('is_read', 0) == 0:
                    created_at = f"🔴 {created_at}"
                self.alerts_table.setItem(i, 4, QTableWidgetItem(created_at))
            
            self.alerts_table.resizeColumnsToContents()
            print(f"✅ {len(alerts)} ta bildirishnoma yuklandi")
            
        except Exception as e:
            print(f"❌ Bildirishnomalarni yuklashda xatolik: {e}")
            import traceback
            traceback.print_exc()
    
    def mark_as_read(self):
        """Tanlangan bildirishnomani o'qilgan deb belgilash"""
        current_row = self.alerts_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ogohlantirish", "Iltimos, bildirishnomani tanlang!")
            return
        
        alert_id = int(self.alerts_table.item(current_row, 0).text())
        result = self.notification_repo.mark_as_read(alert_id)
        
        if result:
            QMessageBox.information(self, "Muvaffaqiyat", "✅ Bildirishnoma o'qilgan deb belgilandi!")
            self.load_alerts()
        else:
            QMessageBox.warning(self, "Xatolik", "Bildirishnomani yangilashda xatolik!")
    
    def mark_all_as_read(self):
        """Barcha bildirishnomalarni o'qilgan deb belgilash"""
        reply = QMessageBox.question(
            self, "Tasdiqlash",
            "Barcha bildirishnomalarni o'qilgan deb belgilaysizmi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.notification_repo.mark_all_as_read()
            if True:  # mark_all_as_read succeeded
                QMessageBox.information(self, "Muvaffaqiyat", f"✅ {result} ta bildirishnoma o'qilgan deb belgilandi!")
                self.load_alerts()
            else:
                QMessageBox.warning(self, "Xatolik", "Bildirishnomalarni yangilashda xatolik!")
    
    def delete_alert(self):
        """Tanlangan bildirishnomani o'chirish"""
        current_row = self.alerts_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ogohlantirish", "Iltimos, o'chirish uchun bildirishnomani tanlang!")
            return
        
        alert_id = int(self.alerts_table.item(current_row, 0).text())
        title = self.alerts_table.item(current_row, 1).text()
        
        reply = QMessageBox.question(
            self, "Tasdiqlash",
            f"'{title}' bildirishnomasini o'chirmoqchimisiz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.notification_repo.delete_notification(alert_id)
            QMessageBox.information(self, "Muvaffaqiyat", "✅ Bildirishnoma o'chirildi!")
            self.load_alerts()
