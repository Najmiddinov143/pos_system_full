# views/reports_view.py - TO'LIQ YANGILANGAN (Sana filtri bilan)

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils.styles import DARK_STYLE
from controllers.report_controller import ReportController
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
import pandas as pd
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

matplotlib.use('Qt5Agg')
matplotlib.rcParams['toolbar'] = 'None'


class ReportsView(QWidget):
    def __init__(self):
        super().__init__()
        self.report_controller = ReportController()
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.load_reports()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ===== HEADER =====
        header_layout = QHBoxLayout()
        title = QLabel("📊 Hisobotlar")
        title.setObjectName("titleLabel")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # ===== SANA FILTRI =====
        filter_widget = QWidget()
        filter_widget.setStyleSheet("background: #1a1a2e; border-radius: 10px; padding: 5px;")
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setSpacing(8)
        filter_layout.setContentsMargins(10, 5, 10, 5)
        
        filter_layout.addWidget(QLabel("📅 Sana:"))
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setDisplayFormat("dd.MM.yyyy")
        self.start_date.setFixedWidth(110)
        self.start_date.setStyleSheet("""
            QDateEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e0e0e0;
            }
            QDateEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        filter_layout.addWidget(self.start_date)
        
        filter_layout.addWidget(QLabel("—"))
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setDisplayFormat("dd.MM.yyyy")
        self.end_date.setFixedWidth(110)
        self.end_date.setStyleSheet("""
            QDateEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e0e0e0;
            }
            QDateEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        filter_layout.addWidget(self.end_date)
        
        # ===== TEZKOR TUGMALAR =====
        btn_today = QPushButton("📅 Bugun")
        btn_today.setObjectName("primaryButton")
        btn_today.setFixedHeight(30)
        btn_today.setStyleSheet("""
            QPushButton#primaryButton {
                background: #6c63ff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#primaryButton:hover {
                background: #5a52d5;
            }
        """)
        btn_today.clicked.connect(self.set_today)
        filter_layout.addWidget(btn_today)
        
        btn_week = QPushButton("📅 7 kun")
        btn_week.setObjectName("primaryButton")
        btn_week.setFixedHeight(30)
        btn_week.setStyleSheet("""
            QPushButton#primaryButton {
                background: #6c63ff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#primaryButton:hover {
                background: #5a52d5;
            }
        """)
        btn_week.clicked.connect(self.set_week)
        filter_layout.addWidget(btn_week)
        
        btn_month = QPushButton("📅 1 oy")
        btn_month.setObjectName("primaryButton")
        btn_month.setFixedHeight(30)
        btn_month.setStyleSheet("""
            QPushButton#primaryButton {
                background: #6c63ff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#primaryButton:hover {
                background: #5a52d5;
            }
        """)
        btn_month.clicked.connect(self.set_month)
        filter_layout.addWidget(btn_month)
        
        btn_year = QPushButton("📅 1 yil")
        btn_year.setObjectName("primaryButton")
        btn_year.setFixedHeight(30)
        btn_year.setStyleSheet("""
            QPushButton#primaryButton {
                background: #6c63ff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#primaryButton:hover {
                background: #5a52d5;
            }
        """)
        btn_year.clicked.connect(self.set_year)
        filter_layout.addWidget(btn_year)
        
        filter_btn = QPushButton("🔍 Filtr")
        filter_btn.setObjectName("primaryButton")
        filter_btn.setFixedHeight(30)
        filter_btn.setStyleSheet("""
            QPushButton#primaryButton {
                background: #00c853;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#primaryButton:hover {
                background: #00e863;
            }
        """)
        filter_btn.clicked.connect(self.load_reports)
        filter_layout.addWidget(filter_btn)
        
        header_layout.addWidget(filter_widget)
        
        # ===== EKSPORT TUGMALARI =====
        export_btn = QPushButton("📤 Excel")
        export_btn.setObjectName("primaryButton")
        export_btn.setMinimumHeight(35)
        export_btn.clicked.connect(self.export_to_excel)
        header_layout.addWidget(export_btn)
        
        pdf_btn = QPushButton("📄 PDF")
        pdf_btn.setObjectName("primaryButton")
        pdf_btn.setMinimumHeight(35)
        pdf_btn.clicked.connect(self.export_to_pdf)
        header_layout.addWidget(pdf_btn)
        
        layout.addLayout(header_layout)
        
        # ===== FOYDA KARTALARI =====
        summary_layout = QHBoxLayout()
        self.summary_cards = {}
        summary_data = [
            ("📈 Bugungi foyda", "today_profit", "0 so'm", "#00c853"),
            ("📊 Haftalik foyda", "weekly_profit", "0 so'm", "#6c63ff"),
            ("📉 Oylik foyda", "monthly_profit", "0 so'm", "#ff9800"),
            ("🏆 Jami foyda", "total_profit", "0 so'm", "#ff6b35")
        ]
        
        for label, key, default, color in summary_data:
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
            label_widget.setStyleSheet(f"font-size: 22px; color: {color}; font-weight: bold;")
            group_layout.addWidget(label_widget)
            summary_layout.addWidget(group)
            self.summary_cards[key] = label_widget
        
        layout.addLayout(summary_layout)
        
        # ===== TO'LOV TURLARI BO'YICHA KARTALAR =====
        payment_layout = QHBoxLayout()
        payment_layout.setSpacing(15)
        
        # Naxt karta
        naxt_group = QGroupBox("💵 Naxt to'lov")
        naxt_group.setStyleSheet("""
            QGroupBox {
                background: #1a1a2e;
                border: 2px solid #00c853;
                border-radius: 12px;
                padding: 10px;
            }
            QGroupBox::title {
                color: #00c853;
                font-weight: bold;
                padding: 0 10px;
            }
        """)
        naxt_layout = QVBoxLayout(naxt_group)
        self.naxt_label = QLabel("0 so'm")
        self.naxt_label.setStyleSheet("font-size: 22px; color: #00c853; font-weight: bold;")
        self.naxt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        naxt_layout.addWidget(self.naxt_label)
        payment_layout.addWidget(naxt_group)
        
        # Plastik karta
        plastik_group = QGroupBox("💳 Plastik to'lov")
        plastik_group.setStyleSheet("""
            QGroupBox {
                background: #1a1a2e;
                border: 2px solid #6c63ff;
                border-radius: 12px;
                padding: 10px;
            }
            QGroupBox::title {
                color: #6c63ff;
                font-weight: bold;
                padding: 0 10px;
            }
        """)
        plastik_layout = QVBoxLayout(plastik_group)
        self.plastik_label = QLabel("0 so'm")
        self.plastik_label.setStyleSheet("font-size: 22px; color: #6c63ff; font-weight: bold;")
        self.plastik_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        plastik_layout.addWidget(self.plastik_label)
        payment_layout.addWidget(plastik_group)
        
        # Aralash to'lov karta
        mixed_group = QGroupBox("💵💳 Naxt+Plastik")
        mixed_group.setStyleSheet("""
            QGroupBox {
                background: #1a1a2e;
                border: 2px solid #ff9800;
                border-radius: 12px;
                padding: 10px;
            }
            QGroupBox::title {
                color: #ff9800;
                font-weight: bold;
                padding: 0 10px;
            }
        """)
        mixed_layout = QVBoxLayout(mixed_group)
        self.mixed_label = QLabel("0 so'm")
        self.mixed_label.setStyleSheet("font-size: 22px; color: #ff9800; font-weight: bold;")
        self.mixed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mixed_layout.addWidget(self.mixed_label)
        payment_layout.addWidget(mixed_group)
        
        # Jami to'lov karta
        total_group = QGroupBox("💰 Jami to'lov")
        total_group.setStyleSheet("""
            QGroupBox {
                background: #1a1a2e;
                border: 2px solid #ffffff;
                border-radius: 12px;
                padding: 10px;
            }
            QGroupBox::title {
                color: #a0a0b8;
                font-weight: bold;
                padding: 0 10px;
            }
        """)
        total_layout = QVBoxLayout(total_group)
        self.total_payment_label = QLabel("0 so'm")
        self.total_payment_label.setStyleSheet("font-size: 22px; color: #ffffff; font-weight: bold;")
        self.total_payment_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_layout.addWidget(self.total_payment_label)
        payment_layout.addWidget(total_group)
        
        layout.addLayout(payment_layout)
        
        # ===== CHARTLAR =====
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        # Foyda grafigi
        profit_group = QGroupBox("Foyda grafigi")
        profit_group.setStyleSheet("""
            QGroupBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 12px;
                padding: 15px;
            }
            QGroupBox::title {
                color: #a0a0b8;
                font-weight: bold;
                padding: 0 10px;
            }
        """)
        profit_layout = QVBoxLayout(profit_group)
        self.profit_canvas = FigureCanvas(Figure(figsize=(6, 4), facecolor='#14142a'))
        self.profit_canvas.figure.patch.set_facecolor('#14142a')
        profit_layout.addWidget(self.profit_canvas)
        charts_layout.addWidget(profit_group)
        
        # To'lov turlari grafigi
        payment_chart_group = QGroupBox("To'lov turlari")
        payment_chart_group.setStyleSheet("""
            QGroupBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 12px;
                padding: 15px;
            }
            QGroupBox::title {
                color: #a0a0b8;
                font-weight: bold;
                padding: 0 10px;
            }
        """)
        payment_chart_layout = QVBoxLayout(payment_chart_group)
        self.payment_canvas = FigureCanvas(Figure(figsize=(6, 4), facecolor='#14142a'))
        self.payment_canvas.figure.patch.set_facecolor('#14142a')
        payment_chart_layout.addWidget(self.payment_canvas)
        charts_layout.addWidget(payment_chart_group)
        
        layout.addLayout(charts_layout)
        
        # ===== ENG KO'P SOTILGAN MAHSULOTLAR =====
        top_products_group = QGroupBox("🏅 Eng ko'p sotilgan mahsulotlar")
        top_products_group.setStyleSheet("""
            QGroupBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 12px;
                padding: 15px;
            }
            QGroupBox::title {
                color: #a0a0b8;
                font-weight: bold;
                padding: 0 10px;
            }
        """)
        top_products_layout = QVBoxLayout(top_products_group)
        self.top_products_table = QTableWidget()
        self.top_products_table.setColumnCount(4)
        self.top_products_table.setHorizontalHeaderLabels([
            'Mahsulot', 'Sotilgan miqdor', 'Jami summa', 'Foyda'
        ])
        self.top_products_table.setStyleSheet("""
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
        top_products_layout.addWidget(self.top_products_table)
        layout.addWidget(top_products_group)
    
    # ============================================================
    # SANA FILTRLARI
    # ============================================================
    def set_today(self):
        today = QDate.currentDate()
        self.start_date.setDate(today)
        self.end_date.setDate(today)
        self.load_reports()
    
    def set_week(self):
        today = QDate.currentDate()
        self.start_date.setDate(today.addDays(-6))
        self.end_date.setDate(today)
        self.load_reports()
    
    def set_month(self):
        today = QDate.currentDate()
        self.start_date.setDate(today.addDays(-29))
        self.end_date.setDate(today)
        self.load_reports()
    
    def set_year(self):
        today = QDate.currentDate()
        self.start_date.setDate(today.addDays(-364))
        self.end_date.setDate(today)
        self.load_reports()
    
    # ============================================================
    # HISOBOTLARNI YUKLASH
    # ============================================================
    def load_reports(self):
        try:
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")
            
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Foyda
            total_profit = self.report_controller.get_total_profit(start, end)
            
            # ===== TO'LOV TURLARI BO'YICHA STATISTIKA =====
            # ===== TO'LOV TURLARI BO'YICHA STATISTIKA =====
            stats = self.report_controller.get_payment_stats(start_date, end_date)
            
            naxt_total = stats.get("naxt_total", 0) + stats.get("mixed_cash", 0)
            plastik_total = stats.get("plastik_total", 0) + stats.get("mixed_card", 0)
            mixed_total = stats.get("mixed_total", 0)
            jami_total = naxt_total + plastik_total + mixed_total
            jami_total = naxt_total + plastik_total + mixed_total
            
            # Kunlar soni
            days = (end - start).days + 1
            
            # ===== KARTALARNI YANGILASH =====
            self.summary_cards['today_profit'].setText(f"{total_profit:,.0f} so'm")
            self.summary_cards['weekly_profit'].setText(f"{total_profit:,.0f} so'm")
            self.summary_cards['monthly_profit'].setText(f"{total_profit:,.0f} so'm")
            self.summary_cards['total_profit'].setText(f"{total_profit:,.0f} so'm")
            
            self.naxt_label.setText(f"💵 {naxt_total:,.0f} so'm")
            self.plastik_label.setText(f"💳 {plastik_total:,.0f} so'm")
            self.mixed_label.setText(f"💵💳 {mixed_total:,.0f} so'm")
            self.total_payment_label.setText(f"💰 {jami_total:,.0f} so'm")
            
            # ===== CHARTLARNI YANGILASH =====
            self.update_charts(start_date, end_date)
            self.update_payment_chart(naxt_total, plastik_total, mixed_total)
            self.update_top_products(start_date, end_date)
            
        except Exception as e:
            print(f"Error loading reports: {e}")
            import traceback
            traceback.print_exc()
    
    # ============================================================
    # CHARTLAR
    # ============================================================
    def update_charts(self, start_date, end_date):
        try:
            # Kunlik foyda
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            days = (end - start).days + 1
            
            # Maksimal 30 kun ko'rsatish (ko'p bo'lsa oylik)
            if days > 30:
                # Oylik ma'lumot
                daily_data = self.report_controller.get_monthly_sales(12)
                if daily_data and daily_data.get('months'):
                    self.plot_monthly_chart(self.profit_canvas, daily_data)
                return
            
            daily_data = []
            for i in range(days):
                d = start + timedelta(days=i)
                profit = self.report_controller.get_total_profit(d, d)
                daily_data.append({
                    'date': d.strftime('%d.%m'),
                    'profit': profit
                })
            
            if daily_data:
                self.plot_profit_chart(self.profit_canvas, daily_data)
        except Exception as e:
            print(f"Error updating charts: {e}")
    
    def plot_monthly_chart(self, canvas, data):
        try:
            fig = canvas.figure
            fig.clear()
            ax = fig.add_subplot(111)
            ax.set_facecolor('#1a1a2e')
            
            months = data.get('months', [])
            amounts = data.get('amounts', [])
            
            bars = ax.bar(months, amounts, color='#00c853', alpha=0.7, edgecolor='white', linewidth=0.5)
            ax.set_xlabel('Oy', color='#a0a0b8', fontsize=11)
            ax.set_ylabel('Foyda (so\'m)', color='#a0a0b8', fontsize=11)
            ax.tick_params(colors='#a0a0b8')
            ax.spines['bottom'].set_color('#2a2a4a')
            ax.spines['left'].set_color('#2a2a4a')
            ax.spines['right'].set_color('#2a2a4a')
            ax.spines['top'].set_color('#2a2a4a')
            ax.grid(axis='y', color='#2a2a4a', linestyle='--', alpha=0.3)
            
            fig.tight_layout()
            canvas.draw()
        except Exception as e:
            print(f"Error plotting monthly chart: {e}")
    
    def plot_profit_chart(self, canvas, data):
        try:
            fig = canvas.figure
            fig.clear()
            ax = fig.add_subplot(111)
            ax.set_facecolor('#1a1a2e')
            
            dates = [d['date'] for d in data]
            profits = [d['profit'] for d in data]
            
            bars = ax.bar(dates, profits, color='#00c853', alpha=0.7, edgecolor='white', linewidth=0.5)
            ax.set_xlabel('Kun', color='#a0a0b8', fontsize=11)
            ax.set_ylabel('Foyda (so\'m)', color='#a0a0b8', fontsize=11)
            ax.tick_params(colors='#a0a0b8')
            ax.spines['bottom'].set_color('#2a2a4a')
            ax.spines['left'].set_color('#2a2a4a')
            ax.spines['right'].set_color('#2a2a4a')
            ax.spines['top'].set_color('#2a2a4a')
            ax.grid(axis='y', color='#2a2a4a', linestyle='--', alpha=0.3)
            
            if profits and max(profits) > 0:
                max_val = max(profits)
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., height + (max_val * 0.02),
                               f'{height:,.0f}',
                               ha='center', va='bottom', color='#e0e0e0', fontsize=8, fontweight='bold')
            
            fig.tight_layout()
            canvas.draw()
        except Exception as e:
            print(f"Error plotting profit chart: {e}")
    
    def update_payment_chart(self, naxt, plastik, mixed):
        try:
            fig = self.payment_canvas.figure
            fig.clear()
            ax = fig.add_subplot(111)
            ax.set_facecolor('#1a1a2e')
            
            labels = ['💵 Naxt', '💳 Plastik', '💵💳 Naxt+Plastik']
            values = [naxt, plastik, mixed]
            colors = ['#00c853', '#6c63ff', '#ff9800']
            
            if sum(values) == 0:
                ax.text(0.5, 0.5, 'Ma\'lumot yo\'q', 
                       ha='center', va='center', color='#a0a0b8', fontsize=16)
            else:
                bars = ax.bar(labels, values, color=colors, alpha=0.8, edgecolor='white', linewidth=0.5)
                
                for bar, val in zip(bars, values):
                    if val > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + (max(values)*0.02),
                               f'{val:,.0f} so\'m',
                               ha='center', va='bottom', color='#e0e0e0', fontsize=9, fontweight='bold')
            
            ax.set_ylabel('Summa (so\'m)', color='#a0a0b8', fontsize=11)
            ax.tick_params(colors='#a0a0b8')
            ax.spines['bottom'].set_color('#2a2a4a')
            ax.spines['left'].set_color('#2a2a4a')
            ax.spines['right'].set_color('#2a2a4a')
            ax.spines['top'].set_color('#2a2a4a')
            
            fig.tight_layout()
            self.payment_canvas.draw()
            
        except Exception as e:
            print(f"Error plotting payment chart: {e}")
    
    def update_top_products(self, start_date, end_date):
        try:
            products = self.report_controller.get_top_products(10)
            
            self.top_products_table.setRowCount(len(products))
            for i, product in enumerate(products):
                self.top_products_table.setItem(i, 0, QTableWidgetItem(str(product.get("name", ""))))
                self.top_products_table.setItem(i, 1, QTableWidgetItem(f"{float(product.get("total_quantity", 0)):.1f}"))
                self.top_products_table.setItem(i, 2, QTableWidgetItem(f"{float(product.get("total_amount", 0)):,.0f} so'm"))
                self.top_products_table.setItem(i, 3, QTableWidgetItem(f"{float(product.get("total_profit", 0)):,.0f} so'm"))
            
            self.top_products_table.setRowCount(len(products))
            for i, product in enumerate(products):
                self.top_products_table.setItem(i, 0, QTableWidgetItem(str(product['name'])))
                self.top_products_table.setItem(i, 1, QTableWidgetItem(f"{product['total_quantity']:.1f}"))
                self.top_products_table.setItem(i, 2, QTableWidgetItem(f"{product['total_amount']:,.0f} so'm"))
                self.top_products_table.setItem(i, 3, QTableWidgetItem(f"{product['total_profit']:,.0f} so'm"))
            
            self.top_products_table.resizeColumnsToContents()
        except Exception as e:
            print(f"Error updating top products: {e}")
    
    # ============================================================
    # EKSPORT
    # ============================================================
    def export_to_excel(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Excel faylni saqlash", "", "Excel Files (*.xlsx)"
            )
            if not file_path:
                return
            
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")
            
            sales_data = self.report_controller.get_sales_for_export(start_date, end_date)

            data = []
            for sale in sales_data:
                for item in sale.get("items", []):
                    subtotal = float(item.get("subtotal", 0))
                    cost_price = float(item.get("cost_price", 0))
                    quantity = float(item.get("quantity", 0))
                    data.append({
                        'Sana': sale.get('created_at', ''),
                        'Mashina': sale.get('car_number', '') or '-',
                        'Mahsulot': item.get('product_name', ''),
                        'Miqdor': quantity,
                        'Narx': item.get('sell_price', 0),
                        'Jami': subtotal,
                        'Foyda': subtotal - (cost_price * quantity),
                        "To'lov turi": sale.get('payment_type', '')
                    })

            if not data:
                QMessageBox.warning(self, "Ogohlantirish", "Eksport qilish uchun ma'lumotlar yo'q!")
                return

            df = pd.DataFrame(data)

            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Savdo', index=False)

                summary = df.groupby("To'lov turi").agg({
                    'Jami': 'sum',
                    'Foyda': 'sum'
                }).reset_index()
                summary.to_excel(writer, sheet_name="To'lov turlari", index=False)

            QMessageBox.information(self, "Muvaffaqiyat", "Excel fayl muvaffaqiyatli saqlandi!")
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Eksport qilishda xatolik: {str(e)}")
    
    def export_to_pdf(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "PDF faylni saqlash", "", "PDF Files (*.pdf)"
            )
            if not file_path:
                return
            
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")
            
            stats = self.report_controller.get_payment_stats(start_date, end_date)
            payment_summary = stats.get("payment_summary", [])

            sales_data = self.report_controller.get_sales_for_export(start_date, end_date)
            
            if not sales_data:
                QMessageBox.warning(self, "Ogohlantirish", "Eksport qilish uchun ma'lumotlar yo'q!")
                return
            
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            title = Paragraph(f"Savdo Hisoboti ({start_date} - {end_date})", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 20))
            
            # To'lov turlari
            if payment_summary:
                story.append(Paragraph("📊 To'lov turlari bo'yicha statistika", styles['Heading2']))
                story.append(Spacer(1, 10))
                
                summary_data = [['To\'lov turi', 'Sotuvlar soni', 'Jami summa', 'Foyda']]
                for row in payment_summary:
                    summary_data.append([
                        row['payment_type'],
                        str(row['count']),
                        f"{row['total']:,.0f} so'm",
                        f"{row['profit']:,.0f} so'm"
                    ])
                
                summary_table = Table(summary_data)
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(summary_table)
                story.append(Spacer(1, 20))
            
            doc.build(story)
            QMessageBox.information(self, "Muvaffaqiyat", "PDF fayl muvaffaqiyatli saqlandi!")
            
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Eksport qilishda xatolik: {str(e)}")