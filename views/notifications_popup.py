# views/notifications_popup.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class NotificationPopup(QWidget):
    def __init__(self, customer_data, parent=None):
        super().__init__(parent)
        self.customer_data = customer_data
        self.setup_ui()
        self.show_animation()
    
    def setup_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(350, 220)
        
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #1a1a2e, stop: 1 #2a2a4a);
                border-radius: 15px;
                border: 2px solid #ff6b35;
            }
        """)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("NAVBAT KELGAN MIJOZ!")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff6b35;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        car_label = QLabel(f"{self.customer_data.get('car_number', '-')}")
        car_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        car_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(car_label)
        
        model = self.customer_data.get('car_model', '')
        if model:
            model_label = QLabel(f"Model: {model}")
            model_label.setStyleSheet("color: #a0a0b8; font-size: 14px;")
            model_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(model_label)
        
        phone = self.customer_data.get('phone_number', '')
        if phone and phone != '-':
            phone_label = QLabel(f"Telefon: {phone}")
            phone_label.setStyleSheet("color: #a0a0b8; font-size: 14px;")
            phone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(phone_label)
        
        date_label = QLabel(f"Keyingi sana: {self.customer_data.get('next_oil_change_date', '-')}")
        date_label.setStyleSheet("color: #a0a0b8; font-size: 14px;")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(date_label)
        
        btn_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("primaryButton")
        ok_btn.clicked.connect(self.close)
        btn_layout.addWidget(ok_btn)
        
        view_btn = QPushButton("Korish")
        view_btn.setObjectName("primaryButton")
        view_btn.clicked.connect(self.go_to_navbat)
        btn_layout.addWidget(view_btn)
        
        layout.addLayout(btn_layout)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(main_widget)
        
        screen = QGuiApplication.primaryScreen().geometry()
        self.move(screen.width() - 380, 50)
    
    def show_animation(self):
        self.show()
        self.raise_()
        self.activateWindow()
        QApplication.beep()
    
    def go_to_navbat(self):
        self.close()
        for widget in QApplication.topLevelWidgets():
            if widget.__class__.__name__ == 'MainWindow':
                widget.show_notifications()
                break