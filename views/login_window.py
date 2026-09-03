# views/login_window.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils.styles import DARK_STYLE
from controllers.auth_controller import AuthController


class LoginWindow(QMainWindow):
    """
    Responsive login oynasi:
    - Oyna o'lchami qattiq belgilanmagan (setFixedSize yo'q).
    - Fon butun oynani qoplaydi, "karta" esa markazda va maksimal
      kenglik bilan cheklangan -> full-screenda ham chiroyli ko'rinadi.
    - Barcha kengayish stretch/QSizePolicy orqali boshqariladi.
    """

    def __init__(self):
        super().__init__()
        self.auth_controller = AuthController()
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self._center_on_screen()

    # ---------------------------------------------------------
    def setup_ui(self):
        self.setWindowTitle("POS Tizimi - Kirish")

        self.setMinimumSize(480, 620)
        self.resize(1100, 760)

        # ===== Fon (butun oynani qoplaydi) =====
        background = QWidget()
        background.setObjectName("loginBackground")
        background.setStyleSheet("""
            QWidget#loginBackground {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #0b0b1a, stop: 0.5 #10102a, stop: 1 #0b0b1a);
            }
        """)
        self.setCentralWidget(background)

        outer_layout = QHBoxLayout(background)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addStretch(1)

        center_col = QVBoxLayout()
        center_col.addStretch(1)

        # ===== Login kartasi =====
        card = QWidget()
        card.setObjectName("loginCard")
        card.setMinimumWidth(380)
        card.setMaximumWidth(440)
        card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        card.setStyleSheet("""
            QWidget#loginCard {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #181832, stop: 1 #14142a);
                border: 1px solid #2a2a4a;
                border-radius: 22px;
            }
        """)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(50)
        shadow.setOffset(0, 14)
        shadow.setColor(QColor(0, 0, 0, 170))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)
        card_layout.setContentsMargins(42, 46, 42, 42)

        logo_wrap = QWidget()
        logo_wrap.setFixedSize(78, 78)
        logo_wrap.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #6c63ff, stop: 1 #4a42d4);
                border-radius: 39px;
            }
        """)
        logo_layout = QVBoxLayout(logo_wrap)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo = QLabel("🏪")
        logo.setStyleSheet("font-size: 36px; background: transparent;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(logo)

        logo_row = QHBoxLayout()
        logo_row.addStretch(1)
        logo_row.addWidget(logo_wrap)
        logo_row.addStretch(1)
        card_layout.addLayout(logo_row)

        card_layout.addSpacing(6)

        title = QLabel("POS Tizimi")
        title.setObjectName("loginTitle")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: white; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        subtitle = QLabel("Moy almashtirish ustalari uchun")
        subtitle.setObjectName("loginSubtitle")
        subtitle.setStyleSheet("font-size: 14px; color: #8a8aa8; background: transparent;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(18)

        field_style = """
            QLineEdit {
                background: #0f0f22;
                border: 2px solid #2a2a4a;
                border-radius: 12px;
                padding: 14px 16px;
                color: #e8e8f5;
                font-size: 15px;
            }
            QLineEdit:focus {
                border: 2px solid #6c63ff;
                background: #14142a;
            }
        """

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("👤 Foydalanuvchi nomi")
        self.username_input.setMinimumHeight(48)
        self.username_input.setStyleSheet(field_style)
        card_layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("🔒 Parol")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(48)
        self.password_input.setStyleSheet(field_style)
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(6)

        login_btn = QPushButton("Kirish")
        login_btn.setObjectName("loginButton")
        login_btn.setMinimumHeight(50)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setStyleSheet("""
            QPushButton#loginButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #6c63ff, stop: 1 #5a52d5);
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 12px;
                border: none;
            }
            QPushButton#loginButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #7c73ff, stop: 1 #6a62e5);
            }
            QPushButton#loginButton:pressed {
                background: #5a52d5;
            }
        """)
        login_btn.clicked.connect(self.login)
        card_layout.addWidget(login_btn)

        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setStyleSheet("font-size: 13px; color: #ff5c5c; background: transparent;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setWordWrap(True)
        card_layout.addWidget(self.error_label)

        # Kartani gorizontal markazlash
        card_row = QHBoxLayout()
        card_row.addStretch(1)
        card_row.addWidget(card)
        card_row.addStretch(1)

        center_col.addLayout(card_row)
        center_col.addStretch(1)

        outer_layout.addLayout(center_col, 0)
        outer_layout.addStretch(1)

        # Enter tugmasi bilan navigatsiya
        self.username_input.returnPressed.connect(lambda: self.password_input.setFocus())
        self.password_input.returnPressed.connect(self.login)

        self.username_input.setFocus()

    # ---------------------------------------------------------
    def _center_on_screen(self):
        screen = QGuiApplication.primaryScreen()
        if not screen:
            return
        geo = screen.availableGeometry()
        x = geo.x() + (geo.width() - self.width()) // 2
        y = geo.y() + (geo.height() - self.height()) // 2
        self.move(max(x, 0), max(y, 0))

    # ---------------------------------------------------------
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.error_label.setText("Iltimos, barcha maydonlarni to'ldiring!")
            return

        user = self.auth_controller.login(username, password)
        if user:
            self.error_label.setText("")
            self.open_main_window(user)
        else:
            self.error_label.setText("❌ Noto'g'ri foydalanuvchi nomi yoki parol!")
            self.password_input.clear()
            self.password_input.setFocus()

    def open_main_window(self, user):
        self.close()
        from views.main_window import MainWindow
        self.main_window = MainWindow(user)
        self.main_window.show()