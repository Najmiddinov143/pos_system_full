# views/password_dialog.py - TO'LIQ TUZATILGAN

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils.styles import DARK_STYLE
import bcrypt


class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.password_correct = False
    
    def setup_ui(self):
        self.setWindowTitle("Parolni tasdiqlang")
        self.setFixedSize(420, 340)
        self.setModal(True)
        self.setStyleSheet("background: #0b0b1a;")
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        # ===== Karta =====
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #181832, stop: 1 #14142a);
            }
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(16)
        layout.setContentsMargins(38, 38, 38, 34)
        
        icon_wrap = QWidget()
        icon_wrap.setFixedSize(70, 70)
        icon_wrap.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #6c63ff, stop: 1 #4a42d4);
                border-radius: 35px;
            }
        """)
        icon_layout = QVBoxLayout(icon_wrap)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel("🔐")
        icon_label.setStyleSheet("font-size: 32px; background: transparent;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon_label)
        
        icon_row = QHBoxLayout()
        icon_row.addStretch(1)
        icon_row.addWidget(icon_wrap)
        icon_row.addStretch(1)
        layout.addLayout(icon_row)
        
        layout.addSpacing(4)
        
        title = QLabel("Himoyalangan bo'lim")
        title.setStyleSheet("font-size: 19px; font-weight: bold; color: #ffffff; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Davom etish uchun parolni kiriting")
        subtitle.setStyleSheet("font-size: 13px; color: #8a8aa8; background: transparent;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(8)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("🔒 Parolni kiriting...")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(48)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background: #0f0f22;
                border: 2px solid #2a2a4a;
                border-radius: 12px;
                padding: 12px 18px;
                color: #e8e8f5;
                font-size: 15px;
            }
            QLineEdit:focus {
                border: 2px solid #6c63ff;
                background: #14142a;
            }
        """)
        self.password_input.returnPressed.connect(self.check_password)
        layout.addWidget(self.password_input)
        
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ff5c5c; font-size: 13px; background: transparent;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)
        
        layout.addSpacing(4)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        cancel_btn = QPushButton("Bekor qilish")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setMinimumHeight(46)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #1a1a32;
                color: #a0a0b8;
                font-weight: 600;
                font-size: 14px;
                border-radius: 11px;
                border: 1px solid #2a2a4a;
            }
            QPushButton:hover {
                background: #22223e;
                color: #e0e0e0;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("Tasdiqlash")
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setMinimumHeight(46)
        ok_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #6c63ff, stop: 1 #5a52d5);
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 11px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #7c73ff, stop: 1 #6a62e5);
            }
        """)
        ok_btn.clicked.connect(self.check_password)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        outer_layout.addWidget(card)
        self.password_input.setFocus()
    
    def check_password(self):
        password = self.password_input.text()
        if not password:
            self.error_label.setText("❌ Iltimos, parolni kiriting!")
            return
        if password == "admin123":
            self.password_correct = True
            self.accept()
        else:
            self.error_label.setText("❌ Noto'g'ri parol! Qayta urinib ko'ring.")
            self.password_input.clear()
            self.password_input.setFocus()
    
    def get_password(self):
        return self.password_input.text()


class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.setModal(True)
    
    def setup_ui(self):
        self.setWindowTitle("Parolni o'zgartirish")
        self.setFixedSize(720, 560)
        self.setStyleSheet("background-color: #0b0f19;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(35, 35, 35, 35)
        
        # ===== SARLAVHA =====
        title_widget = QWidget()
        title_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #1e293b, stop: 1 #0f172a);
                border: 1px solid #334155;
                border-radius: 16px;
            }
        """)
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(20, 15, 20, 15)
        
        icon_label = QLabel("🔐")
        icon_label.setStyleSheet("font-size: 28px; background: transparent; border: none;")
        title_layout.addWidget(icon_label)
        
        title_label = QLabel("Admin parolini o'zgartirish")
        title_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #f8fafc; background: transparent; border: none;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        main_layout.addWidget(title_widget)
        
        # ===== FORM MATRITSA =====
        form_widget = QWidget()
        form_widget.setStyleSheet("""
            QWidget {
                background: #111827;
                border: 1px solid #1f2937;
                border-radius: 16px;
            }
        """)
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(25, 25, 25, 25)
        
        input_stylesheet = """
            QLineEdit {
                background: #1f2937;
                border: 2px solid #374151;
                border-radius: 10px;
                padding: 12px 16px;
                color: #f3f4f6;
                font-size: 15px;
            }
            QLineEdit:focus {
                border: 2px solid #6366f1;
                background: #111827;
            }
            QLineEdit::placeholder {
                color: #6b7280;
            }
        """
        label_stylesheet = "color: #9ca3af; font-size: 14px; font-weight: 600; background: transparent; border: none;"
        
        # 1-QATOR: Eski va Yangi parol
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(20)
        
        # Eski parol
        old_layout = QVBoxLayout()
        old_label = QLabel("🔑 Eski parol")
        old_label.setStyleSheet(label_stylesheet)
        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.old_password.setPlaceholderText("Eski parolni kiriting")
        self.old_password.setStyleSheet(input_stylesheet)
        old_layout.addWidget(old_label)
        old_layout.addWidget(self.old_password)
        row1_layout.addLayout(old_layout)
        
        # Yangi parol
        new_layout = QVBoxLayout()
        new_label = QLabel("🆕 Yangi parol")
        new_label.setStyleSheet(label_stylesheet)
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password.setPlaceholderText("Yangi parolni kiriting")
        self.new_password.setStyleSheet(input_stylesheet)
        new_layout.addWidget(new_label)
        new_layout.addWidget(self.new_password)
        row1_layout.addLayout(new_layout)
        
        form_layout.addLayout(row1_layout)
        
        # 2-QATOR: Parolni tasdiqlash
        row2_layout = QHBoxLayout()
        confirm_layout = QVBoxLayout()
        confirm_label = QLabel("✅ Parolni tasdiqlang")
        confirm_label.setStyleSheet(label_stylesheet)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password.setPlaceholderText("Parolni qayta kiriting")
        self.confirm_password.setStyleSheet(input_stylesheet)
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_password)
        row2_layout.addLayout(confirm_layout)
        row2_layout.addSpacing(20)
        row2_layout.addStretch()
        form_layout.addLayout(row2_layout)
        
        main_layout.addWidget(form_widget)
        
        # ===== STATUS LABELS =====
        status_layout = QHBoxLayout()
        
        self.strength_label = QLabel("")
        self.strength_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #10b981; background: transparent;")
        self.new_password.textChanged.connect(self.check_password_strength)
        status_layout.addWidget(self.strength_label)
        
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ef4444; font-size: 14px; font-weight: 500; background: transparent;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        status_layout.addWidget(self.error_label)
        
        main_layout.addLayout(status_layout)
        
        # ===== TUGMALAR =====
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Bekor qilish")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #1f2937;
                color: #9ca3af;
                font-weight: 600;
                font-size: 15px;
                padding: 12px 28px;
                border-radius: 10px;
                border: 1px solid #374151;
            }
            QPushButton:hover {
                background: #374151;
                color: #f3f4f6;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Saqlash")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4f46e5;
                color: white;
                font-weight: 600;
                font-size: 15px;
                padding: 12px 32px;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background: #4338ca;
            }
        """)
        save_btn.clicked.connect(self.change_password)
        button_layout.addWidget(save_btn)
        
        main_layout.addLayout(button_layout)
        
        # ===== ESLATMA =====
        info_label = QLabel("💡 Parol kamida 4 ta belgidan iborat bo'lishi kerak")
        info_label.setStyleSheet("color: #4b5563; font-size: 13px; background: transparent;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info_label)
    
    def check_password_strength(self):
        password = self.new_password.text()
        if not password:
            self.strength_label.setText("")
            return
        
        strength = 0
        if len(password) >= 4:
            strength += 1
        if len(password) >= 8:
            strength += 1
        if any(c.isdigit() for c in password):
            strength += 1
        if any(c.isupper() for c in password):
            strength += 1
        if any(c in "!@#$%^&*" for c in password):
            strength += 1
        
        if strength <= 1:
            self.strength_label.setText("⚠️ Zaif parol")
            self.strength_label.setStyleSheet("font-size: 13px; font-weight: bold; background: #3a1a1a; color: #ff5252; padding: 6px 14px; border-radius: 8px;")
        elif strength <= 3:
            self.strength_label.setText("⚠️ O'rtacha parol")
            self.strength_label.setStyleSheet("font-size: 13px; font-weight: bold; background: #3a3a1a; color: #ffd54f; padding: 6px 14px; border-radius: 8px;")
        else:
            self.strength_label.setText("✅ Kuchli parol")
            self.strength_label.setStyleSheet("font-size: 13px; font-weight: bold; background: #1a3a1a; color: #4caf50; padding: 6px 14px; border-radius: 8px;")
    
    def change_password(self):
        try:
            old = self.old_password.text().strip()
            new = self.new_password.text().strip()
            confirm = self.confirm_password.text().strip()
            
            if not old or not new:
                self.error_label.setText("❌ Iltimos, barcha maydonlarni to'ldiring!")
                return
            
            if new != confirm:
                self.error_label.setText("❌ Yangi parollar mos kelmadi!")
                return
            
            if len(new) < 4:
                self.error_label.setText("❌ Parol 4 ta belgidan kam bo'lmasin!")
                return
            
            from models.repositories import UserRepository
            user_repo = UserRepository()
            result = user_repo.change_password(old, new)
            
            if result and not result.get("error"):
                QMessageBox.information(
                    self, 
                    "Muvaffaqiyat", 
                    "✅ Parol muvaffaqiyatli o'zgartirildi!\n\n🔐 Xavfsizlik uchun tizimdan chiqasiz va qayta kirasiz."
                )
                
                self.accept()
                
                parent = self.parent()
                while parent:
                    if parent.__class__.__name__ == 'MainWindow':
                        parent.close()
                        from views.login_window import LoginWindow
                        login = LoginWindow()
                        login.show()
                        break
                    parent = parent.parent()
            else:
                detail = result.get("detail", "Noma'lum xatolik") if result else "API xatosi"
                self.error_label.setText(f"❌ {detail}")
                
        except Exception as e:
            self.error_label.setText(f"❌ Xatolik: {str(e)}")
            print(f"Error: {e}")