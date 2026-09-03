# utils/styles.py
# ============================================================
#  ZAMONAVIY "MIDNIGHT PREMIUM" DIZAYN TIZIMI
#  - Barcha o'lcham/rang/shrift bitta joydan boshqariladi
#  - Full-screen / kichraytirilgan holatda ham buzilmaydi,
#    chunki kengayish view'lardagi Layout stretch orqali
#    boshqariladi, bu yerda esa faqat vizual til beriladi.
# ============================================================

# ---- Rang palitrasi (bitta joyda, kerak bo'lsa shu yerdan o'zgartiring) ----
COLOR_BG            = "#0b0e16"   # asosiy fon
COLOR_BG_SOFT       = "#0f1320"   # bir oz ochroq fon (panel orqasi)
COLOR_SURFACE       = "#141a29"   # kartalar / panel yuzasi
COLOR_SURFACE_ALT   = "#1b2233"   # ikkinchi darajali panel
COLOR_BORDER        = "#232b3d"   # standart border
COLOR_BORDER_SOFT   = "#1c2333"

COLOR_ACCENT        = "#7c6cff"   # asosiy aksent (binafsha-indigo)
COLOR_ACCENT_HOVER  = "#8f80ff"
COLOR_ACCENT_DARK   = "#5b4fd6"

COLOR_SUCCESS       = "#22c55e"
COLOR_SUCCESS_DARK  = "#16a34a"
COLOR_DANGER        = "#ef4444"
COLOR_DANGER_DARK   = "#c92f2f"
COLOR_WARNING       = "#f59e0b"
COLOR_WARNING_DARK  = "#c2790a"

COLOR_TEXT          = "#e7e9ee"
COLOR_TEXT_MUTED    = "#8b93a7"
COLOR_TEXT_FAINT    = "#5b6478"

# ---- O'lcham skalasi ----
RADIUS_SM  = "8px"
RADIUS_MD  = "12px"
RADIUS_LG  = "16px"
CTRL_H     = "44px"   # input/tugma standart balandligi

DARK_STYLE = f"""
/* ================= GLOBAL ================= */
* {{
    font-family: 'Segoe UI', 'Inter', 'Roboto', Arial, sans-serif;
    outline: none;
}}

QWidget {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT};
    font-size: 14px;
}}

QMainWindow {{
    background-color: {COLOR_BG};
}}

QToolTip {{
    background-color: {COLOR_SURFACE_ALT};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 6px 10px;
}}

/* ================= SIDEBAR / TOOLBAR ================= */
QToolBar {{
    background-color: {COLOR_BG_SOFT};
    border: none;
    border-right: 1px solid {COLOR_BORDER_SOFT};
    spacing: 4px;
    padding: 14px 10px;
}}

QToolBar QToolButton {{
    background-color: transparent;
    border: none;
    border-radius: {RADIUS_MD};
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 600;
    color: {COLOR_TEXT_MUTED};
    min-width: 190px;
    min-height: 20px;
}}

QToolBar QToolButton:hover {{
    background-color: {COLOR_SURFACE_ALT};
    color: {COLOR_TEXT};
}}

QToolBar QToolButton:checked {{
    background-color: rgba(124, 108, 255, 0.16);
    color: #ffffff;
    border-left: 3px solid {COLOR_ACCENT};
    padding-left: 13px;
}}

QToolBar QToolButton:pressed {{
    background-color: rgba(124, 108, 255, 0.25);
}}

QToolBar::separator {{
    background: {COLOR_BORDER_SOFT};
    height: 1px;
    margin: 10px 8px;
}}

/* ================= HEADER / TITLE ================= */
QLabel#titleLabel {{
    font-size: 26px;
    font-weight: 700;
    color: #ffffff;
    padding: 4px 0;
    background: transparent;
    letter-spacing: 0.2px;
}}

QLabel#subtitleLabel {{
    font-size: 15px;
    color: {COLOR_TEXT_MUTED};
    background: transparent;
}}

/* ================= CARDS ================= */
QWidget#cardWidget {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 {COLOR_SURFACE}, stop: 1 {COLOR_SURFACE_ALT});
    border-radius: {RADIUS_LG};
    padding: 16px;
    border: 1px solid {COLOR_BORDER};
}}

QLabel#cardTitle {{
    font-size: 13px;
    color: {COLOR_TEXT_MUTED};
    font-weight: 600;
    letter-spacing: 0.4px;
    background: transparent;
}}

QLabel#cardValue {{
    font-size: 26px;
    font-weight: 700;
    color: #ffffff;
    background: transparent;
}}

/* ================= BUTTONS ================= */
QPushButton {{
    background: {COLOR_SURFACE_ALT};
    border: 1px solid {COLOR_BORDER};
    border-radius: {RADIUS_MD};
    padding: 10px 20px;
    min-height: {CTRL_H};
    font-weight: 600;
    font-size: 14px;
    color: {COLOR_TEXT};
}}

QPushButton:hover {{
    background: #242c40;
    border-color: {COLOR_ACCENT_DARK};
}}

QPushButton:pressed {{
    background: #2b3350;
}}

QPushButton:disabled {{
    color: {COLOR_TEXT_FAINT};
    background: {COLOR_SURFACE};
    border-color: {COLOR_BORDER_SOFT};
}}

QPushButton#primaryButton {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 {COLOR_ACCENT}, stop: 1 {COLOR_ACCENT_DARK});
    color: white;
    border: none;
}}
QPushButton#primaryButton:hover {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 {COLOR_ACCENT_HOVER}, stop: 1 {COLOR_ACCENT});
}}

QPushButton#successButton {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 {COLOR_SUCCESS}, stop: 1 {COLOR_SUCCESS_DARK});
    color: white;
    border: none;
}}
QPushButton#successButton:hover {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #34d071, stop: 1 {COLOR_SUCCESS});
}}

QPushButton#dangerButton {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 {COLOR_DANGER}, stop: 1 {COLOR_DANGER_DARK});
    color: white;
    border: none;
}}
QPushButton#dangerButton:hover {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #f65f5f, stop: 1 {COLOR_DANGER});
}}

QPushButton#warningButton {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 {COLOR_WARNING}, stop: 1 {COLOR_WARNING_DARK});
    color: #1a1300;
    border: none;
}}
QPushButton#warningButton:hover {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #ffb733, stop: 1 {COLOR_WARNING});
}}

/* ================= INPUTS ================= */
QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
    background: {COLOR_SURFACE};
    border: 1.5px solid {COLOR_BORDER};
    border-radius: {RADIUS_MD};
    padding: 10px 14px;
    min-height: {CTRL_H};
    color: {COLOR_TEXT};
    font-size: 14px;
    selection-background-color: {COLOR_ACCENT};
}}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QDateEdit:focus {{
    border: 1.5px solid {COLOR_ACCENT};
    background: {COLOR_SURFACE_ALT};
}}

QLineEdit::placeholder {{
    color: {COLOR_TEXT_FAINT};
}}

QComboBox::drop-down {{
    border: none;
    width: 32px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid {COLOR_TEXT_MUTED};
    margin-right: 10px;
}}
QComboBox QAbstractItemView {{
    background: {COLOR_SURFACE_ALT};
    border: 1px solid {COLOR_BORDER};
    border-radius: {RADIUS_SM};
    selection-background-color: {COLOR_ACCENT};
    color: {COLOR_TEXT};
    padding: 6px;
    outline: none;
}}

QCheckBox {{
    color: {COLOR_TEXT};
    spacing: 10px;
    padding: 4px;
    background: transparent;
}}
QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 6px;
    border: 1.5px solid {COLOR_BORDER};
    background: {COLOR_SURFACE};
}}
QCheckBox::indicator:checked {{
    background: {COLOR_ACCENT};
    border-color: {COLOR_ACCENT};
}}

/* ================= TABLES ================= */
QTableWidget {{
    background: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    border-radius: {RADIUS_MD};
    gridline-color: {COLOR_BORDER_SOFT};
    alternate-background-color: {COLOR_SURFACE_ALT};
    selection-background-color: transparent;
}}

QTableWidget::item {{
    padding: 10px;
    border: none;
}}
QTableWidget::item:selected {{
    background: rgba(124, 108, 255, 0.25);
    color: #ffffff;
}}
QTableWidget::item:hover {{
    background: rgba(124, 108, 255, 0.10);
}}

QHeaderView::section {{
    background: {COLOR_SURFACE_ALT};
    padding: 12px 10px;
    border: none;
    border-bottom: 2px solid {COLOR_BORDER};
    color: {COLOR_TEXT_MUTED};
    font-weight: 700;
    font-size: 12.5px;
    letter-spacing: 0.3px;
}}

/* ================= GROUPBOX ================= */
QGroupBox {{
    border: 1px solid {COLOR_BORDER};
    border-radius: {RADIUS_MD};
    margin-top: 16px;
    padding-top: 16px;
    background: {COLOR_SURFACE};
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px;
    color: {COLOR_TEXT_MUTED};
    font-weight: 700;
    font-size: 13.5px;
}}

/* ================= SCROLLBARS ================= */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {COLOR_SURFACE_ALT};
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLOR_ACCENT_DARK};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: {COLOR_SURFACE_ALT};
    border-radius: 5px;
    min-width: 30px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ================= DIALOG / MESSAGEBOX ================= */
QDialog {{
    background: {COLOR_BG};
}}
QMessageBox {{
    background: {COLOR_SURFACE};
}}
QMessageBox QPushButton {{
    min-width: 90px;
}}

/* ================= STATUS BAR ================= */
QStatusBar {{
    background: {COLOR_BG_SOFT};
    color: {COLOR_TEXT_MUTED};
    border-top: 1px solid {COLOR_BORDER_SOFT};
    padding: 6px 18px;
    font-size: 13px;
}}

/* ================= LIST WIDGET ================= */
QListWidget {{
    background: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    border-radius: {RADIUS_MD};
    padding: 6px;
}}
QListWidget::item {{
    padding: 12px 14px;
    border-radius: {RADIUS_SM};
    margin: 2px 0;
}}
QListWidget::item:selected {{
    background: rgba(124, 108, 255, 0.28);
    color: white;
}}
QListWidget::item:hover {{
    background: rgba(255,255,255,0.04);
}}

/* ================= KARTA RANGLARI (DASHBOARD) ================= */
QWidget#cardBlue {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #1c2b6b, stop: 1 #10173e);
    border-radius: {RADIUS_LG};
    padding: 16px;
}}
QWidget#cardGreen {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #146b3a, stop: 1 #0c331e);
    border-radius: {RADIUS_LG};
    padding: 16px;
}}
QWidget#cardRed {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #9c1f1f, stop: 1 #4c0f0f);
    border-radius: {RADIUS_LG};
    padding: 16px;
}}
QWidget#cardOrange {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #b5590a, stop: 1 #5c2c04);
    border-radius: {RADIUS_LG};
    padding: 16px;
}}
QWidget#cardPurple {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #5a2e9e, stop: 1 #2c1652);
    border-radius: {RADIUS_LG};
    padding: 16px;
}}
QWidget#cardTeal {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #0e6b5c, stop: 1 #08332c);
    border-radius: {RADIUS_LG};
    padding: 16px;
}}

/* ================= LOGIN ================= */
QWidget#loginBackground {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #0b0e16, stop: 0.5 #0d1226, stop: 1 #131a33);
}}

QWidget#loginCard {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 {COLOR_SURFACE}, stop: 1 {COLOR_SURFACE_ALT});
    border-radius: 22px;
    border: 1px solid {COLOR_BORDER};
}}

QLabel#loginTitle {{
    font-size: 30px;
    font-weight: 800;
    color: #ffffff;
    background: transparent;
}}

QLabel#loginSubtitle {{
    font-size: 14.5px;
    color: {COLOR_TEXT_MUTED};
    background: transparent;
}}

QPushButton#loginButton {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 {COLOR_ACCENT}, stop: 1 {COLOR_ACCENT_DARK});
    color: white;
    font-weight: 700;
    font-size: 16px;
    min-height: 50px;
    border-radius: 14px;
    border: none;
}}
QPushButton#loginButton:hover {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 {COLOR_ACCENT_HOVER}, stop: 1 {COLOR_ACCENT});
}}

/* ================= SELL BUTTON ================= */
QPushButton#sellButton {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 {COLOR_SUCCESS}, stop: 1 {COLOR_SUCCESS_DARK});
    color: white;
    font-weight: 700;
    font-size: 16px;
    min-height: 56px;
    border-radius: {RADIUS_MD};
    border: none;
}}
QPushButton#sellButton:hover {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #34d071, stop: 1 {COLOR_SUCCESS});
}}

/* ================= LABELS ================= */
QLabel#errorLabel {{
    color: {COLOR_DANGER};
    font-weight: 600;
}}
QLabel#successLabel {{
    color: {COLOR_SUCCESS};
    font-weight: 600;
}}
"""

# Alohida kartalar uchun mustaqil stil (eski kod bilan moslik uchun saqlanadi)
CARD_STYLE = f"""
QWidget#cardWidget {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 {COLOR_SURFACE}, stop: 1 {COLOR_SURFACE_ALT});
    border-radius: {RADIUS_LG};
    padding: 16px;
    border: 1px solid {COLOR_BORDER};
}}

QLabel#cardTitle {{
    font-size: 13px;
    color: {COLOR_TEXT_MUTED};
    font-weight: 600;
}}

QLabel#cardValue {{
    font-size: 26px;
    font-weight: 700;
    color: #ffffff;
}}
"""