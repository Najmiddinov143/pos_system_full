# # views/expenses_view.py
# from PyQt6.QtWidgets import *
# from PyQt6.QtCore import *
# from PyQt6.QtGui import *
# from utils.styles import DARK_STYLE
# from controllers.expense_controller import ExpenseController
# from models.models import Expense
# from datetime import datetime, timedelta

# class ExpensesView(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.expense_controller = ExpenseController()
#         self.setup_ui()
#         self.setStyleSheet(DARK_STYLE)
#         self.load_expenses()
    
    


#     def setup_ui(self):
#         layout = QVBoxLayout(self)
#         layout.setSpacing(15)
#         layout.setContentsMargins(20, 20, 20, 20)
        
#         # Header
#         header_layout = QHBoxLayout()
#         title = QLabel("💰 Xarajatlar")
#         title.setObjectName("titleLabel")
#         title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
#         header_layout.addWidget(title)
        
#         header_layout.addStretch()
        
#         add_btn = QPushButton("➕ Yangi xarajat")
#         add_btn.setObjectName("primaryButton")
#         add_btn.clicked.connect(self.show_add_expense_dialog)
#         header_layout.addWidget(add_btn)
        
#         layout.addLayout(header_layout)
        
#         # Statistics
#         stats_layout = QHBoxLayout()
#         self.stats_labels = {}
#         stats = [
#             ("📊 Jami xarajat", "total", "0 so'm"),
#             ("📈 Bugun", "today", "0 so'm"),
#             ("📉 Oylik", "month", "0 so'm")
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
#             label_widget.setStyleSheet("font-size: 22px; color: #ff6b35; font-weight: bold;")
#             group_layout.addWidget(label_widget)
#             stats_layout.addWidget(group)
#             self.stats_labels[key] = label_widget
        
#         layout.addLayout(stats_layout)
        
#         # Table
#         self.table = QTableWidget()
#         self.table.setColumnCount(6)
#         self.table.setHorizontalHeaderLabels([
#             'ID', 'Sana', 'Nomi', 'Kategoriya', 'Summa', 'Izoh'
#         ])
#         self.table.setStyleSheet("""
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
#         self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
#         self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
#         self.table.horizontalHeader().setStretchLastSection(True)
#         layout.addWidget(self.table)
        
#         # Buttons
#         button_layout = QHBoxLayout()
        
#         delete_btn = QPushButton("🗑️ O'chirish")
#         delete_btn.setObjectName("dangerButton")
#         delete_btn.clicked.connect(self.delete_expense)
#         button_layout.addWidget(delete_btn)
        
#         refresh_btn = QPushButton("🔄 Yangilash")
#         refresh_btn.setObjectName("primaryButton")
#         refresh_btn.clicked.connect(self.load_expenses)
#         button_layout.addWidget(refresh_btn)
        
#         layout.addLayout(button_layout)
    
#     def load_expenses(self):
#         try:
#             expenses = self.expense_controller.get_all_expenses()
            
#             self.table.setRowCount(len(expenses))
            
#             total = 0
#             today = datetime.now().strftime('%Y-%m-%d')
#             month = datetime.now().strftime('%Y-%m')
#             today_total = 0
#             month_total = 0
            
#             for i, exp in enumerate(expenses):
#                 self.table.setItem(i, 0, QTableWidgetItem(str(exp['id'])))
#                 self.table.setItem(i, 1, QTableWidgetItem(exp['created_at'][:16] if exp['created_at'] else ''))
#                 self.table.setItem(i, 2, QTableWidgetItem(exp['name']))
#                 self.table.setItem(i, 3, QTableWidgetItem(exp['category']))
#                 self.table.setItem(i, 4, QTableWidgetItem(f"{exp['amount']:,.0f} so'm"))
#                 self.table.setItem(i, 5, QTableWidgetItem(exp['description'] or '-'))
                
#                 total += exp['amount']
#                 if exp['created_at'] and exp['created_at'].startswith(today):
#                     today_total += exp['amount']
#                 if exp['created_at'] and exp['created_at'].startswith(month):
#                     month_total += exp['amount']
            
#             self.stats_labels['total'].setText(f"{total:,.0f} so'm")
#             self.stats_labels['today'].setText(f"{today_total:,.0f} so'm")
#             self.stats_labels['month'].setText(f"{month_total:,.0f} so'm")
            
#             self.table.resizeColumnsToContents()
#         except Exception as e:
#             print(f"Error loading expenses: {e}")
    
#     def show_add_expense_dialog(self):
#         dialog = ExpenseDialog(self)
#         if dialog.exec() == QDialog.DialogCode.Accepted:
#             self.load_expenses()
    
#     def delete_expense(self):
#         selected = self.table.currentRow()
#         if selected < 0:
#             QMessageBox.warning(self, "Ogohlantirish", "Iltimos, o'chirish uchun xarajat tanlang!")
#             return
        
#         expense_id = int(self.table.item(selected, 0).text())
#         expense_name = self.table.item(selected, 2).text()
        
#         reply = QMessageBox.question(
#             self, "Tasdiqlash",
#             f"'{expense_name}' xarajatini o'chirmoqchimisiz?",
#             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
#         )
        
#         if reply == QMessageBox.StandardButton.Yes:
#             self.expense_controller.delete_expense(expense_id)
#             self.load_expenses()


# class ExpenseDialog(QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setup_ui()
#         self.setStyleSheet(DARK_STYLE)
    
#     def setup_ui(self):
#         self.setWindowTitle("Yangi xarajat qo'shish")
#         self.setFixedSize(450, 400)
        
#         layout = QVBoxLayout(self)
#         layout.setSpacing(15)
#         layout.setContentsMargins(25, 25, 25, 25)
        
#         form_layout = QFormLayout()
#         form_layout.setSpacing(12)
        
#         # Name
#         self.name_input = QLineEdit()
#         self.name_input.setPlaceholderText("Mas: Ishchi oyligi")
#         form_layout.addRow("Nomi:", self.name_input)
        
#         # Category
#         self.category_input = QComboBox()
#         categories = [
#             "👨‍💼 Ishchi oyligi",
#             "🏠 Kommunal",
#             "📢 Reklama",
#             "🚚 Transport",
#             "🔧 Ta'mirlash",
#             "📦 Materiallar",
#             "💻 Kompyuter",
#             "📱 Telefon",
#             "💰 Boshqa"
#         ]
#         self.category_input.addItems(categories)
#         form_layout.addRow("Kategoriya:", self.category_input)
        
#         # Amount
#         self.amount_input = QDoubleSpinBox()
#         self.amount_input.setRange(0, 1000000000)
#         self.amount_input.setPrefix("so'm ")
#         self.amount_input.setStyleSheet("""
#             QDoubleSpinBox {
#                 background: #1a1a2e;
#                 border: 2px solid #2a2a4a;
#                 border-radius: 8px;
#                 padding: 8px 12px;
#                 color: #e0e0e0;
#             }
#             QDoubleSpinBox:focus {
#                 border: 2px solid #6c63ff;
#             }
#         """)
#         form_layout.addRow("Summa:", self.amount_input)
        
#         # Description
#         self.description_input = QTextEdit()
#         self.description_input.setMaximumHeight(80)
#         self.description_input.setPlaceholderText("Qo'shimcha ma'lumot...")
#         form_layout.addRow("Izoh:", self.description_input)
        
#         layout.addLayout(form_layout)
        
#         # Buttons
#         button_layout = QHBoxLayout()
        
#         save_btn = QPushButton("💾 Saqlash")
#         save_btn.setObjectName("primaryButton")
#         save_btn.setMinimumHeight(40)
#         save_btn.clicked.connect(self.save_expense)
#         button_layout.addWidget(save_btn)
        
#         cancel_btn = QPushButton("❌ Bekor qilish")
#         cancel_btn.clicked.connect(self.reject)
#         button_layout.addWidget(cancel_btn)
        
#         layout.addLayout(button_layout)
    
#     def save_expense(self):
#         name = self.name_input.text().strip()
#         if not name:
#             QMessageBox.warning(self, "Xatolik", "Iltimos, xarajat nomini kiriting!")
#             return
        
#         amount = self.amount_input.value()
#         if amount <= 0:
#             QMessageBox.warning(self, "Xatolik", "Iltimos, summani kiriting!")
#             return
        
#         expense = Expense(
#             name=name,
#             amount=amount,
#             category=self.category_input.currentText(),
#             description=self.description_input.toPlainText().strip()
#         )
        
#         controller = ExpenseController()
#         controller.create_expense(expense)
#         self.accept()



# views/expenses_view.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils.styles import DARK_STYLE
from controllers.expense_controller import ExpenseController
from models.models import Expense
from datetime import datetime

class ExpensesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.expense_controller = ExpenseController()
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.load_expenses()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        title = QLabel("💰 Xarajatlar")
        title.setObjectName("titleLabel")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        add_btn = QPushButton("➕ Yangi xarajat")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self.show_add_expense_dialog)
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)
        
        stats_layout = QHBoxLayout()
        self.stats_labels = {}
        stats = [("📊 Jami xarajat", "total", "0 so'm"), ("📈 Bugun", "today", "0 so'm"), ("📉 Oylik", "month", "0 so'm")]
        
        for label, key, default in stats:
            group = QGroupBox(label)
            group.setStyleSheet("""
                QGroupBox {
                    background: #1a1a2e;
                    border: 2px solid #2a2a4a;
                    border-radius: 12px;
                    padding: 10px;
                }
                QGroupBox::title {
                    color: #a0a0b8;
                    font-weight: bold;
                    padding: 0 10px;
                }
            """)
            group_layout = QVBoxLayout(group)
            label_widget = QLabel(default)
            label_widget.setObjectName("cardValue")
            label_widget.setStyleSheet("font-size: 22px; color: #ff6b35; font-weight: bold;")
            group_layout.addWidget(label_widget)
            stats_layout.addWidget(group)
            self.stats_labels[key] = label_widget
        
        layout.addLayout(stats_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['ID', 'Sana', 'Nomi', 'Kategoriya', 'Summa', 'Kassa', 'Izoh'])
        self.table.setStyleSheet("""
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
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        button_layout = QHBoxLayout()
        delete_btn = QPushButton("🗑️ O'chirish")
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(self.delete_expense)
        button_layout.addWidget(delete_btn)
        
        refresh_btn = QPushButton("🔄 Yangilash")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.clicked.connect(self.load_expenses)
        button_layout.addWidget(refresh_btn)
        layout.addLayout(button_layout)
    
    def load_expenses(self):
        try:
            expenses = self.expense_controller.get_all_expenses()
            self.table.setRowCount(len(expenses))
            total = 0
            today = datetime.now().strftime('%Y-%m-%d')
            month = datetime.now().strftime('%Y-%m')
            today_total = 0
            month_total = 0
            
            for i, exp in enumerate(expenses):
                self.table.setItem(i, 0, QTableWidgetItem(str(exp['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(exp['created_at'][:16] if exp['created_at'] else ''))
                self.table.setItem(i, 2, QTableWidgetItem(exp['name']))
                self.table.setItem(i, 3, QTableWidgetItem(exp['category']))
                self.table.setItem(i, 4, QTableWidgetItem(f"{exp['amount']:,.0f} so'm"))
                payment_type = exp['payment_type'] if 'payment_type' in exp.keys() and exp['payment_type'] else 'Naxt'
                kassa_text = "💳 Plastik" if payment_type == 'Plastik' else "💵 Naxt"
                self.table.setItem(i, 5, QTableWidgetItem(kassa_text))
                self.table.setItem(i, 6, QTableWidgetItem(exp['description'] or '-'))
                
                total += exp['amount']
                if exp['created_at'] and exp['created_at'].startswith(today):
                    today_total += exp['amount']
                if exp['created_at'] and exp['created_at'].startswith(month):
                    month_total += exp['amount']
            
            self.stats_labels['total'].setText(f"{total:,.0f} so'm")
            self.stats_labels['today'].setText(f"{today_total:,.0f} so'm")
            self.stats_labels['month'].setText(f"{month_total:,.0f} so'm")
            self.table.resizeColumnsToContents()
        except Exception as e:
            print(f"Error loading expenses: {e}")
    
    def show_add_expense_dialog(self):
        dialog = ExpenseDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_expenses()
    
    def delete_expense(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ogohlantirish", "Iltimos, o'chirish uchun xarajat tanlang!")
            return
        expense_id = int(self.table.item(selected, 0).text())
        expense_name = self.table.item(selected, 2).text()
        reply = QMessageBox.question(self, "Tasdiqlash", f"'{expense_name}' xarajatini o'chirmoqchimisiz?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.expense_controller.delete_expense(expense_id)
            self.load_expenses()

class ExpenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
    
    def setup_ui(self):
        self.setWindowTitle("Yangi xarajat qo'shish")
        self.setFixedSize(460, 560)
        self.setStyleSheet(self.styleSheet() + """
            QDialog { background: #14142a; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(28, 26, 28, 26)
        
        title = QLabel("💰 Yangi xarajat")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; background: transparent;")
        layout.addWidget(title)
        
        # Barcha input turlariga bir xil, keng va o'qilishi oson uslub
        field_style = """
            QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 10px;
                padding: 11px 14px;
                color: #e0e0e0;
                font-size: 14px;
                min-height: 22px;
            }
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
                border: 2px solid #6c63ff;
                background: #1e1e38;
            }
            QComboBox::drop-down { border: none; width: 28px; }
            QComboBox QAbstractItemView {
                background: #1a1a2e;
                color: #e0e0e0;
                selection-background-color: #4a4a8a;
                padding: 4px;
                outline: none;
            }
        """
        label_style = "color: #a0a0b8; font-size: 13px; font-weight: 600; background: transparent;"
        
        def add_field(text, widget):
            lbl = QLabel(text)
            lbl.setStyleSheet(label_style)
            layout.addWidget(lbl)
            widget.setStyleSheet(field_style)
            layout.addWidget(widget)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Mas: Ishchi oyligi")
        self.name_input.setMinimumHeight(44)
        add_field("Nomi:", self.name_input)
        
        self.category_input = QComboBox()
        categories = ["👨‍💼 Ishchi oyligi", "🏠 Kommunal", "📢 Reklama", "🚚 Transport", "🔧 Ta'mirlash", "📦 Materiallar", "💻 Kompyuter", "📱 Telefon", "💰 Boshqa"]
        self.category_input.addItems(categories)
        self.category_input.setMinimumHeight(44)
        add_field("Kategoriya:", self.category_input)
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 1000000000)
        self.amount_input.setPrefix("so'm ")
        self.amount_input.setMinimumHeight(44)
        add_field("Summa:", self.amount_input)
        
        self.payment_type_input = QComboBox()
        self.payment_type_input.addItems(['💵 Naxt', '💳 Plastik'])
        self.payment_type_input.setMinimumHeight(44)
        add_field("Qaysi kassadan:", self.payment_type_input)
        
        self.description_input = QTextEdit()
        self.description_input.setFixedHeight(80)
        self.description_input.setPlaceholderText("Qo'shimcha ma'lumot...")
        add_field("Izoh:", self.description_input)
        
        layout.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        save_btn = QPushButton("💾 Saqlash")
        save_btn.setObjectName("primaryButton")
        save_btn.setMinimumHeight(46)
        save_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        save_btn.clicked.connect(self.save_expense)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Bekor qilish")
        cancel_btn.setMinimumHeight(46)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def save_expense(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Xatolik", "Iltimos, xarajat nomini kiriting!")
            return
        amount = self.amount_input.value()
        if amount <= 0:
            QMessageBox.warning(self, "Xatolik", "Iltimos, summani kiriting!")
            return
        payment_type = self.payment_type_input.currentText().split(" ", 1)[-1].strip()
        expense = Expense(name=name, amount=amount, category=self.category_input.currentText(), description=self.description_input.toPlainText().strip(), payment_type=payment_type)
        controller = ExpenseController()
        controller.create_expense(expense)
        self.accept()