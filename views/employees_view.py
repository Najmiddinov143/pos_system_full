# views/employees_view.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils.styles import DARK_STYLE
from models.repositories import EmployeeRepository
from models.models import Employee
from datetime import datetime

class EmployeesView(QWidget):
    def __init__(self):
        super().__init__()
        self.employee_repo = EmployeeRepository()
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.load_employees()
        
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        title = QLabel("👥 Xodimlar")
        title.setObjectName("titleLabel")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        add_btn = QPushButton("➕ Yangi xodim")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self.show_add_employee_dialog)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Statistics
        stats_layout = QHBoxLayout()
        self.stats_labels = {}
        stats = [
            ("👥 Jami xodimlar", "total", "0"),
            ("📌 Faol", "active", "0"),
            ("📊 Ishda", "working", "0")
        ]
        
        for label, key, default in stats:
            group = QGroupBox(label)
            group.setStyleSheet("""
                QGroupBox {
                    background: #1a1a2e;
                    border: 2px solid #2a2a4a;
                    border-radius: 12px;
                    padding: 10px;
                }
            """)
            group_layout = QVBoxLayout(group)
            label_widget = QLabel(default)
            label_widget.setObjectName("cardValue")
            label_widget.setStyleSheet("font-size: 22px; color: #6c63ff; font-weight: bold;")
            group_layout.addWidget(label_widget)
            stats_layout.addWidget(group)
            self.stats_labels[key] = label_widget
        
        layout.addLayout(stats_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'ID', 'F.I.O', 'Telefon', 'Lavozim', 'Oylik', 'Ishga kirgan', 'Holat'
        ])
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
        """)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        check_in_btn = QPushButton("📥 Ishga kelish")
        check_in_btn.setObjectName("successButton")
        check_in_btn.clicked.connect(self.check_in)
        button_layout.addWidget(check_in_btn)
        
        check_out_btn = QPushButton("📤 Ishdan chiqish")
        check_out_btn.setObjectName("dangerButton")
        check_out_btn.clicked.connect(self.check_out)
        button_layout.addWidget(check_out_btn)
        
        delete_btn = QPushButton("🗑️ O'chirish")
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(self.delete_employee)
        button_layout.addWidget(delete_btn)
        
        refresh_btn = QPushButton("🔄 Yangilash")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.clicked.connect(self.load_employees)
        button_layout.addWidget(refresh_btn)
        
        layout.addLayout(button_layout)
    
    def load_employees(self):
        try:
            employees = self.employee_repo.get_all_employees()
            
            self.table.setRowCount(len(employees))
            
            total = len(employees)
            active = 0
            today = datetime.now().strftime("%Y-%m-%d")
            working = 0
            
            for i, emp in enumerate(employees):
                self.table.setItem(i, 0, QTableWidgetItem(str(emp['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(emp['full_name']))
                self.table.setItem(i, 2, QTableWidgetItem(emp['phone'] or '-'))
                self.table.setItem(i, 3, QTableWidgetItem(emp['position']))
                self.table.setItem(i, 4, QTableWidgetItem(f"{emp['salary']:,.0f} so'm"))
                self.table.setItem(i, 5, QTableWidgetItem(emp['hire_date'] or '-'))
                
                status = "✅ Faol" if emp['is_active'] else "❌ No faol"
                self.table.setItem(i, 6, QTableWidgetItem(status))
                
                if emp['is_active']:
                    active += 1
                    # Ishga kelganmi tekshirish
                    attendance = self.employee_repo.get_attendance(emp['id'], today)
                    if attendance and attendance['check_in']:
                        working += 1
            
            self.stats_labels['total'].setText(str(total))
            self.stats_labels['active'].setText(str(active))
            self.stats_labels['working'].setText(str(working))
            
            self.table.resizeColumnsToContents()
        except Exception as e:
            print(f"Error loading employees: {e}")
    
    def show_add_employee_dialog(self):
        dialog = EmployeeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_employees()
    
    def check_in(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ogohlantirish", "Iltimos, xodimni tanlang!")
            return
        
        employee_id = int(self.table.item(selected, 0).text())
        employee_name = self.table.item(selected, 1).text()
        
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().strftime("%H:%M:%S")
        
        self.employee_repo.check_in(employee_id, today, now)
        QMessageBox.information(self, "Muvaffaqiyat", f"✅ {employee_name} ishga keldi! ({now})")
        self.load_employees()
    
    def check_out(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ogohlantirish", "Iltimos, xodimni tanlang!")
            return
        
        employee_id = int(self.table.item(selected, 0).text())
        employee_name = self.table.item(selected, 1).text()
        
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().strftime("%H:%M:%S")
        
        self.employee_repo.check_out(employee_id, today, now)
        QMessageBox.information(self, "Muvaffaqiyat", f"✅ {employee_name} ishdan chiqdi! ({now})")
        self.load_employees()
    
    def delete_employee(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ogohlantirish", "Iltimos, xodimni tanlang!")
            return
        
        employee_id = int(self.table.item(selected, 0).text())
        employee_name = self.table.item(selected, 1).text()
        
        reply = QMessageBox.question(
            self, "Tasdiqlash",
            f"'{employee_name}' xodimini o'chirmoqchimisiz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.employee_repo.delete_employee(employee_id)
            self.load_employees()


class EmployeeDialog(QDialog):
    def __init__(self, parent=None, employee_data=None):
        super().__init__(parent)
        self.employee_data = employee_data
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.load_data()
    
    def setup_ui(self):
        self.setWindowTitle("Yangi xodim" if not self.employee_data else "Xodimni tahrirlash")
        self.setFixedSize(400, 500)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("To'liq ismi")
        form_layout.addRow("F.I.O:", self.name_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+998 99 123 45 67")
        form_layout.addRow("Telefon:", self.phone_input)
        
        self.position_input = QComboBox()
        positions = ['Admin', 'Kassir', 'Omborchi', 'Hisobchi', 'Usta', 'Tozalovchi']
        self.position_input.addItems(positions)
        form_layout.addRow("Lavozim:", self.position_input)
        
        self.salary_input = QDoubleSpinBox()
        self.salary_input.setRange(0, 100000000)
        self.salary_input.setPrefix("so'm ")
        form_layout.addRow("Oylik:", self.salary_input)
        
        self.hire_date_input = QDateEdit()
        self.hire_date_input.setCalendarPopup(True)
        self.hire_date_input.setDate(QDate.currentDate())
        form_layout.addRow("Ishga kirgan sana:", self.hire_date_input)
        
        layout.addLayout(form_layout)
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Saqlash")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self.save_employee)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Bekor qilish")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_data(self):
        if self.employee_data:
            self.name_input.setText(self.employee_data['full_name'])
            self.phone_input.setText(self.employee_data['phone'] or '')
            self.position_input.setCurrentText(self.employee_data['position'])
            self.salary_input.setValue(self.employee_data['salary'])
            if self.employee_data['hire_date']:
                self.hire_date_input.setDate(QDate.fromString(self.employee_data['hire_date'], "yyyy-MM-dd"))
    
    def save_employee(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Xatolik", "Iltimos, xodim ismini kiriting!")
            return
        
        employee = Employee(
            full_name=name,
            phone=self.phone_input.text().strip(),
            position=self.position_input.currentText(),
            salary=self.salary_input.value(),
            hire_date=self.hire_date_input.date().toString("yyyy-MM-dd")
        )
        
        repo = EmployeeRepository()
        if self.employee_data:
            employee.id = self.employee_data['id']
            employee.is_active = self.employee_data['is_active']
            repo.update_employee(employee)
        else:
            repo.create_employee(employee)
        
        self.accept()