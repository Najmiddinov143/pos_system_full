# views/main_window.py - QIZIL NUQTA TO'G'RI ISHLAYDI

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils.styles import DARK_STYLE
from views.dashboard import Dashboard
from views.product_management import ProductManagement
from views.pos_view import POSView
from views.sales_history import SalesHistory
from views.reports_view import ReportsView
from views.inventory_view import InventoryView
from views.notifications_view import NotificationsView
from views.alerts_view import AlertsView
from views.expenses_view import ExpensesView
from views.password_dialog import PasswordDialog
from views.employees_view import EmployeesView
from views.backup_view import BackupView
from views.shop_settings_view import SettingsView
from views.sms_view import SMSView
from controllers.notification_controller import NotificationController
from models.repositories import PurchaseRepository, ProductRepository
from datetime import datetime, timedelta



class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.notification_controller = NotificationController()
        self.purchase_repo = PurchaseRepository()
        self.product_repo = ProductRepository()
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        
        if self.user.role == 'admin':
            self.show_dashboard()
        else:
            self.show_pos()
        
        # Har 30 soniyada barcha nuqtalarni yangilash
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all_dots)
        self.timer.start(30000)
        
        QTimer.singleShot(1000, self.update_all_dots)
    
    def setup_ui(self):
        self.setWindowTitle("POS Tizimi - Moy almashtirish")
        self.setGeometry(100, 50, 1500, 900)
        
        self.central_widget = QStackedWidget()
        self.central_widget.setStyleSheet("background: #0f0f0f;")
        self.setCentralWidget(self.central_widget)
        
        # ===== BARCHA SAHIFALAR =====
        self.dashboard = Dashboard(self.user)
        self.product_management = ProductManagement()
        self.pos_view = POSView(self.user)
        self.sales_history = SalesHistory()
        self.reports_view = ReportsView()
        self.inventory_view = InventoryView()
        self.notifications_view = NotificationsView()
        self.alerts_view = AlertsView()
        self.expenses_view = ExpensesView()
        self.employees_view = EmployeesView()
        self.backup_view = BackupView()
        self.shop_settings_view = SettingsView()
        self.sms_view = SMSView()
        
        # ===== STACKED WIDGET GA QO'SHISH =====
        self.central_widget.addWidget(self.dashboard)          # 0
        self.central_widget.addWidget(self.product_management) # 1
        self.central_widget.addWidget(self.pos_view)           # 2
        self.central_widget.addWidget(self.sales_history)      # 3
        self.central_widget.addWidget(self.reports_view)       # 4
        self.central_widget.addWidget(self.inventory_view)     # 5
        self.central_widget.addWidget(self.notifications_view) # 6
        self.central_widget.addWidget(self.alerts_view)        # 7
        self.central_widget.addWidget(self.expenses_view)      # 8
        self.central_widget.addWidget(self.employees_view)     # 9
        self.central_widget.addWidget(self.backup_view)        # 10
        self.central_widget.addWidget(self.shop_settings_view) # 11
        self.central_widget.addWidget(self.sms_view)           # 12
        
        self.create_sidebar()
        
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background: #14142a;
                color: #a0a0b8;
                border-top: 1px solid #2a2a4a;
                padding: 8px 20px;
                font-size: 13px;
            }
        """)
        self.update_status()
        
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)
    
    def update_status(self):
        self.statusBar().showMessage(
            f"👤 {self.user.username} ({self.user.role.upper()})  |  🕐 {QDateTime.currentDateTime().toString('dd.MM.yyyy HH:mm:ss')}"
        )
    
    def update_all_dots(self):
        """Barcha menyulardagi nuqtalarni yangilash"""
        try:
            # 1. Navbat - o'qilmagan bildirishnomalar
            unread_count = self.notification_controller.get_unread_count()
            
            # 2. Ombor - kam qolgan mahsulotlar
            low_stock_count = self.get_low_stock_count()
            
            # 3. Bildirishnomalar - to'lanmagan qarzlar + kam mahsulot
            unpaid_debts = self.get_unpaid_debts()
            alert_count = len(unpaid_debts) + low_stock_count
            
            # 4. Ombor uchun alohida: qarzlar + kam mahsulot
            ombor_count = len(unpaid_debts) + low_stock_count
            
            for btn in self.nav_buttons:
                text = btn.text()
                
                # ===== NAVBAT =====
                if "Navbat" in text:
                    if unread_count > 0:
                        btn.setText("🔔 Navbat 🔴")
                        btn.setStyleSheet(self._get_active_style())
                    else:
                        btn.setText("🔔 Navbat")
                        btn.setStyleSheet(self._get_normal_style())
                
                # ===== OMBOR =====
                elif "Ombor" in text:
                    if ombor_count > 0:
                        btn.setText("🏪 Ombor 🔴")
                        btn.setStyleSheet(self._get_active_style())
                    else:
                        btn.setText("🏪 Ombor")
                        btn.setStyleSheet(self._get_normal_style())
                
                # ===== BILDIRISHNOMALAR =====
                elif "Bildirishnomalar" in text:
                    if alert_count > 0:
                        btn.setText("📬 Bildirishnomalar 🔴")
                        btn.setStyleSheet(self._get_active_style())
                    else:
                        btn.setText("📬 Bildirishnomalar")
                        btn.setStyleSheet(self._get_normal_style())
            
            print(f"🔔 Dots: Navbat={unread_count}, Ombor={ombor_count}, Bildirishnomalar={alert_count}")
            
        except Exception as e:
            print(f"❌ Dots yangilashda xatolik: {e}")
    
    def _get_active_style(self):
        return """
            QToolButton {
                background: #2a1a2a;
                border: none;
                border-radius: 10px;
                padding: 12px 15px;
                text-align: left;
                font-size: 14px;
                font-weight: 500;
                color: #ff6b6b;
            }
            QToolButton:hover {
                background: #3a2a3a;
                color: #ff6b6b;
            }
        """
    
    def _get_normal_style(self):
        return """
            QToolButton {
                background: transparent;
                border: none;
                border-radius: 10px;
                padding: 12px 15px;
                text-align: left;
                font-size: 14px;
                font-weight: 500;
                color: #a0a0b8;
            }
            QToolButton:hover {
                background: #2a2a4a;
                color: #ffffff;
            }
        """
    
    def get_low_stock_count(self):
        """Kam qolgan mahsulotlar soni (quantity <= min_quantity)"""
        try:
            products = self.product_repo.get_all()
            count = 0
            if products:
                for product in products:
                    if isinstance(product, dict):
                        qty = product.get('quantity', 0)
                        min_qty = product.get('min_quantity', 5)
                    else:
                        qty = getattr(product, 'quantity', 0)
                        min_qty = getattr(product, 'min_quantity', 5)
                    
                    # 🔥 Kam qolgan: quantity <= min_quantity
                    if qty <= min_qty:
                        count += 1
            return count
        except Exception as e:
            print(f"❌ Kam qolganlarni olishda xatolik: {e}")
            return 0
    
    def get_unpaid_debts(self):
        """To'lanmagan qarzlar (is_paid = 0)"""
        try:
            all_debts = self.purchase_repo.get_all_purchases_with_debts()
            unpaid = []
            today = datetime.now().date()
            
            if all_debts:
                for debt in all_debts:
                    if isinstance(debt, dict):
                        is_paid = debt.get('is_paid', 0)
                    else:
                        is_paid = getattr(debt, 'is_paid', 0)
                    
                    # 🔥 Faqat to'lanmaganlar (is_paid = 0)
                    if is_paid == 0:
                        unpaid.append(debt)
            
            return unpaid
        except Exception as e:
            print(f"❌ Qarzlarni olishda xatolik: {e}")
            return []
    
    def get_alert_count(self):
        """Ogohlantirishlar soni (qarzlar + kam mahsulot)"""
        unpaid = self.get_unpaid_debts()
        low_stock = self.get_low_stock_count()
        return len(unpaid) + low_stock
    
    def create_sidebar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background: #1a1a2e;
                border: none;
                spacing: 2px;
                padding: 10px 5px;
                min-width: 60px;
            }
            QToolButton {
                background: transparent;
                border: none;
                border-radius: 10px;
                padding: 12px 15px;
                text-align: left;
                font-size: 14px;
                font-weight: 500;
                color: #a0a0b8;
            }
            QToolButton:hover {
                background: #2a2a4a;
                color: #ffffff;
            }
            QToolButton:checked {
                background: #4a4a8a;
                color: #ffffff;
                border-left: 3px solid #6c63ff;
            }
        """)
        toolbar.setOrientation(Qt.Orientation.Vertical)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, toolbar)
        
        nav_items = [
            ("📊", "Dashboard", self.show_dashboard, 0),
            ("🔔", "Navbat", self.show_notifications, 1),
            ("🛒", "Sotuv", self.show_pos, 2),
            ("📦", "Mahsulotlar", self.show_products, 3),
            ("📋", "Savdo tarixi", self.show_sales_history, 4),
            ("💰", "Xarajatlar", self.show_expenses, 5),
            ("👥", "Xodimlar", self.show_employees, 6),
            ("💾", "Zaxiralash", self.show_backup, 7),
            ("📬", "Bildirishnomalar", self.show_alerts, 8),
            ("📱", "SMS", self.show_sms, 9),
            ("📈", "Hisobotlar", self.show_reports, 10),
            ("🏪", "Ombor", self.show_inventory, 11),
            ("⚙️", "Sozlamalar", self.show_shop_settings, 12)
        ]
        
        self.nav_buttons = []
        for icon, text, callback, index in nav_items:
            btn = QToolButton()
            
            if self.user.role == 'cashier' and text in ['Dashboard', 'Navbat', 'Hisobotlar', 'Ombor', 'Xarajatlar', 'Xodimlar', 'Zaxiralash', 'Bildirishnomalar', 'SMS', 'Sozlamalar']:
                btn.setText(f"{icon} {text} 🔒")
                btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
                btn.setCheckable(True)
                btn.setProperty("nav_index", index)
                btn.clicked.connect(callback)
                toolbar.addWidget(btn)
                self.nav_buttons.append(btn)
                continue
            
            btn.setText(f"{icon} {text}")
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            btn.setCheckable(True)
            btn.setProperty("nav_index", index)
            btn.clicked.connect(callback)
            toolbar.addWidget(btn)
            self.nav_buttons.append(btn)
        
        toolbar.addSeparator()
        
        logout_btn = QToolButton()
        logout_btn.setText("🚪 Chiqish")
        logout_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        logout_btn.setStyleSheet("""
            QToolButton { color: #ff5252; }
            QToolButton:hover { background: #3a1a1a; }
        """)
        logout_btn.clicked.connect(self.logout)
        toolbar.addWidget(logout_btn)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.addWidget(spacer)
    
    def show_dashboard(self):
        if self.user.role == 'admin':
            self.central_widget.setCurrentWidget(self.dashboard)
            self.update_nav_buttons(0)
            return
        password_dialog = PasswordDialog(self)
        if password_dialog.exec() == QDialog.DialogCode.Accepted:
            self.central_widget.setCurrentWidget(self.dashboard)
            self.update_nav_buttons(0)
    
    def show_notifications(self):
        if self.user.role == 'admin':
            self.central_widget.setCurrentWidget(self.notifications_view)
            self.update_nav_buttons(1)
            self.notifications_view.load_notifications()
            QTimer.singleShot(500, self.update_all_dots)
            return
        password_dialog = PasswordDialog(self)
        if password_dialog.exec() == QDialog.DialogCode.Accepted:
            self.central_widget.setCurrentWidget(self.notifications_view)
            self.update_nav_buttons(1)
            self.notifications_view.load_notifications()
            QTimer.singleShot(500, self.update_all_dots)
    
    def show_pos(self):
        self.central_widget.setCurrentWidget(self.pos_view)
        self.update_nav_buttons(2)
        self.pos_view.load_products()
    
    def show_products(self):
        self.central_widget.setCurrentWidget(self.product_management)
        self.update_nav_buttons(3)
        self.product_management.load_products()
    
    def show_sales_history(self):
        self.central_widget.setCurrentWidget(self.sales_history)
        self.update_nav_buttons(4)
        self.sales_history.load_sales()
    
    def show_expenses(self):
        if self.user.role == 'admin':
            self.central_widget.setCurrentWidget(self.expenses_view)
            self.update_nav_buttons(5)
            self.expenses_view.load_expenses()
            return
        password_dialog = PasswordDialog(self)
        if password_dialog.exec() == QDialog.DialogCode.Accepted:
            self.central_widget.setCurrentWidget(self.expenses_view)
            self.update_nav_buttons(5)
            self.expenses_view.load_expenses()
    
    def show_employees(self):
        if self.user.role == 'admin':
            self.central_widget.setCurrentWidget(self.employees_view)
            self.update_nav_buttons(6)
            self.employees_view.load_employees()
            return
        password_dialog = PasswordDialog(self)
        if password_dialog.exec() == QDialog.DialogCode.Accepted:
            self.central_widget.setCurrentWidget(self.employees_view)
            self.update_nav_buttons(6)
            self.employees_view.load_employees()
    
    def show_backup(self):
        if self.user.role == 'admin':
            self.central_widget.setCurrentWidget(self.backup_view)
            self.update_nav_buttons(7)
            self.backup_view.load_backup_history()
            return
        password_dialog = PasswordDialog(self)
        if password_dialog.exec() == QDialog.DialogCode.Accepted:
            self.central_widget.setCurrentWidget(self.backup_view)
            self.update_nav_buttons(7)
            self.backup_view.load_backup_history()
    
    def show_alerts(self):
        if self.user.role == 'admin':
            self.central_widget.setCurrentWidget(self.alerts_view)
            self.update_nav_buttons(8)
            self.alerts_view.load_alerts()
            QTimer.singleShot(500, self.update_all_dots)
            return
        password_dialog = PasswordDialog(self)
        if password_dialog.exec() == QDialog.DialogCode.Accepted:
            self.central_widget.setCurrentWidget(self.alerts_view)
            self.update_nav_buttons(8)
            self.alerts_view.load_alerts()
            QTimer.singleShot(500, self.update_all_dots)
    
    def show_sms(self):
        if self.user.role == 'admin':
            self.central_widget.setCurrentWidget(self.sms_view)
            self.update_nav_buttons(9)
            self.sms_view.load_customers()
            return
        password_dialog = PasswordDialog(self)
        if password_dialog.exec() == QDialog.DialogCode.Accepted:
            self.central_widget.setCurrentWidget(self.sms_view)
            self.update_nav_buttons(9)
            self.sms_view.load_customers()
    
    def show_reports(self):
        if self.user.role == 'admin':
            self.central_widget.setCurrentWidget(self.reports_view)
            self.update_nav_buttons(10)
            self.reports_view.load_reports()
            return
        password_dialog = PasswordDialog(self)
        if password_dialog.exec() == QDialog.DialogCode.Accepted:
            self.central_widget.setCurrentWidget(self.reports_view)
            self.update_nav_buttons(10)
            self.reports_view.load_reports()
    
    def show_inventory(self):
        if self.user.role == 'admin':
            self.central_widget.setCurrentWidget(self.inventory_view)
            self.update_nav_buttons(11)
            self.inventory_view.load_inventory_data()
            QTimer.singleShot(500, self.update_all_dots)
            return
        password_dialog = PasswordDialog(self)
        if password_dialog.exec() == QDialog.DialogCode.Accepted:
            self.central_widget.setCurrentWidget(self.inventory_view)
            self.update_nav_buttons(11)
            self.inventory_view.load_inventory_data()
            QTimer.singleShot(500, self.update_all_dots)
    
    def show_shop_settings(self):
        if self.user.role == 'admin':
            self.central_widget.setCurrentWidget(self.shop_settings_view)
            self.update_nav_buttons(12)
            self.shop_settings_view.load_settings()
            return
        password_dialog = PasswordDialog(self)
        if password_dialog.exec() == QDialog.DialogCode.Accepted:
            self.central_widget.setCurrentWidget(self.shop_settings_view)
            self.update_nav_buttons(12)
            self.shop_settings_view.load_settings()
    
    def update_nav_buttons(self, index):
        for btn in self.nav_buttons:
            btn.setChecked(btn.property("nav_index") == index)
    
    def logout(self):
        reply = QMessageBox.question(
            self, "Chiqish",
            "Tizimdan chiqmoqchimisiz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            from views.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()