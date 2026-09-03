# from PyQt6.QtWidgets import *
# from PyQt6.QtCore import *
# from PyQt6.QtGui import *
# from utils.styles import DARK_STYLE
# from controllers.sale_controller import SaleController
# from controllers.product_controller import ProductController
# from datetime import datetime
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import A6
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER, TA_RIGHT

# class ReceiptDialog(QDialog):
#     def __init__(self, sale_id, parent=None):
#         super().__init__(parent)
#         self.sale_id = sale_id
#         self.sale_controller = SaleController()
#         self.product_controller = ProductController()
#         self.setup_ui()
#         self.setStyleSheet(DARK_STYLE)
#         self.load_receipt_data()
    
#     def setup_ui(self):
#         self.setWindowTitle("🧾 Chek")
#         self.setFixedSize(400, 600)
        
#         layout = QVBoxLayout(self)
        
#         # Receipt preview
#         self.receipt_text = QTextEdit()
#         self.receipt_text.setReadOnly(True)
#         self.receipt_text.setFont(QFont("Courier", 10))
#         layout.addWidget(self.receipt_text)
        
#         # Buttons
#         button_layout = QHBoxLayout()
        
#         print_btn = QPushButton("🖨️ Chop etish")
#         print_btn.setObjectName("primaryButton")
#         print_btn.clicked.connect(self.print_receipt)
#         button_layout.addWidget(print_btn)
        
#         pdf_btn = QPushButton("📄 PDF saqlash")
#         pdf_btn.clicked.connect(self.save_pdf)
#         button_layout.addWidget(pdf_btn)
        
#         close_btn = QPushButton("❌ Yopish")
#         close_btn.clicked.connect(self.accept)
#         button_layout.addWidget(close_btn)
        
#         layout.addLayout(button_layout)
    
# # views/receipt_view.py - load_receipt_data metodini tuzatamiz
# def load_receipt_data(self):
#     try:
#         sale = self.sale_controller.get_sale_by_id(self.sale_id)
#         if not sale:
#             self.receipt_text.setText("Chek ma'lumotlari topilmadi!")
#             return
        
#         items = self.sale_controller.get_sale_items(self.sale_id)
        
#         # Format receipt
#         receipt = []
#         receipt.append("=" * 40)
#         receipt.append("        🏪 POS TIZIMI")
#         receipt.append("        Moy almashtirish")
#         receipt.append("=" * 40)
#         receipt.append("")
        
#         # Handle date safely
#         created_at = sale.get('created_at', '')
#         if created_at and hasattr(created_at, 'strftime'):
#             receipt.append(f"Sana: {created_at.strftime('%Y-%m-%d %H:%M')}")
#         else:
#             receipt.append(f"Sana: {created_at}")
        
#         receipt.append(f"Chek №: {sale.get('id', 0):06d}")
#         receipt.append("")
#         receipt.append("-" * 40)
#         receipt.append(f"{'Mahsulot':<20} {'Narx':>8} {'Miq':>5} {'Jami':>10}")
#         receipt.append("-" * 40)
        
#         for item in items:
#             name = item.get('product_name', '')[:18]
#             if len(item.get('product_name', '')) > 18:
#                 name += ".."
            
#             receipt.append(
#                 f"{name:<20} "
#                 f"{item.get('sell_price', 0):>8.0f} "
#                 f"{item.get('quantity', 0):>5.1f} "
#                 f"{item.get('subtotal', 0):>10.0f}"
#             )
        
#         receipt.append("-" * 40)
#         receipt.append(f"{'Jami:':<34} {sale.get('total_amount', 0):>10.0f}")
        
#         if sale.get('discount', 0) > 0:
#             receipt.append(f"{'Chegirma:':<34} {sale.get('discount', 0):>10.0f}%")
#             receipt.append(f"{'Yakuniy:':<34} {sale.get('total_amount', 0):>10.0f}")
        
#         receipt.append("")
#         receipt.append("=" * 40)
#         receipt.append("     Rahmat! Xush kelibsiz!")
#         receipt.append("=" * 40)
        
#         self.receipt_text.setText("\n".join(receipt))
        
#         # Store data for printing/PDF
#         self.sale = sale
#         self.items = items
#         self.receipt_lines = receipt
        
#     except Exception as e:
#         print(f"Error loading receipt: {e}")
#         self.receipt_text.setText(f"Xatolik: {str(e)}")
#     try:
#         sale = self.sale_controller.get_sale_by_id(self.sale_id)
#         if not sale:
#             self.receipt_text.setText("Chek ma'lumotlari topilmadi!")
#             return
        
#         items = self.sale_controller.get_sale_items(self.sale_id)
        
#         # Format receipt
#         receipt = []
#         receipt.append("=" * 40)
#         receipt.append("        🏪 POS TIZIMI")
#         receipt.append("        Moy almashtirish")
#         receipt.append("=" * 40)
#         receipt.append("")
        
#         # Handle date properly
#         created_at = sale.get('created_at', '')
#         if created_at and hasattr(created_at, 'strftime'):
#             receipt.append(f"Sana: {created_at.strftime('%Y-%m-%d %H:%M')}")
#         else:
#             receipt.append(f"Sana: {created_at}")
        
#         receipt.append(f"Chek №: {sale['id']:06d}")
#         receipt.append("")
#         receipt.append("-" * 40)
#         receipt.append(f"{'Mahsulot':<20} {'Narx':>8} {'Miq':>5} {'Jami':>10}")
#         receipt.append("-" * 40)
        
#         for item in items:
#             name = item['product_name'][:18]  # Truncate long names
#             if len(item['product_name']) > 18:
#                 name += ".."
            
#             receipt.append(
#                 f"{name:<20} "
#                 f"{item['sell_price']:>8.0f} "
#                 f"{item['quantity']:>5.1f} "
#                 f"{item['subtotal']:>10.0f}"
#             )
        
#         receipt.append("-" * 40)
#         receipt.append(f"{'Jami:':<34} {sale['total_amount']:>10.0f}")
        
#         if sale.get('discount', 0) > 0:
#             receipt.append(f"{'Chegirma:':<34} {sale['discount']:>10.0f}%")
#             receipt.append(f"{'Yakuniy:':<34} {sale['total_amount']:>10.0f}")
        
#         receipt.append("")
#         receipt.append("=" * 40)
#         receipt.append("     Rahmat! Xush kelibsiz!")
#         receipt.append("=" * 40)
        
#         self.receipt_text.setText("\n".join(receipt))
        
#         # Store data for printing/PDF
#         self.sale = sale
#         self.items = items
#         self.receipt_lines = receipt
        
#     except Exception as e:
#         print(f"Error loading receipt: {e}")
#         self.receipt_text.setText(f"Xatolik: {str(e)}")
        
#         sale = self.sale_controller.get_sale_by_id(self.sale_id)
#         if not sale:
#             self.receipt_text.setText("Chek ma'lumotlari topilmadi!")
#             return
        
#         items = self.sale_controller.get_sale_items(self.sale_id)
        
#         # Format receipt
#         receipt = []
#         receipt.append("=" * 40)
#         receipt.append("        🏪 POS TIZIMI")
#         receipt.append("        Moy almashtirish")
#         receipt.append("=" * 40)
#         receipt.append("")
#         receipt.append(f"Sana: {sale['created_at']}")
#         receipt.append(f"Chek №: {sale['id']:06d}")
#         receipt.append("")
#         receipt.append("-" * 40)
#         receipt.append(f"{'Mahsulot':<20} {'Narx':>8} {'Miq':>5} {'Jami':>10}")
#         receipt.append("-" * 40)
        
#         for item in items:
#             name = item['product_name'][:18]  # Truncate long names
#             if len(item['product_name']) > 18:
#                 name += ".."
            
#             receipt.append(
#                 f"{name:<20} "
#                 f"{item['sell_price']:>8.0f} "
#                 f"{item['quantity']:>5.1f} "
#                 f"{item['subtotal']:>10.0f}"
#             )
        
#         receipt.append("-" * 40)
#         receipt.append(f"{'Jami:':<34} {sale['total_amount']:>10.0f}")
        
#         if sale['discount'] > 0:
#             receipt.append(f"{'Chegirma:':<34} {sale['discount']:>10.0f}%")
#             receipt.append(f"{'Yakuniy:':<34} {sale['total_amount']:>10.0f}")
        
#         receipt.append("")
#         receipt.append("=" * 40)
#         receipt.append("     Rahmat! Xush kelibsiz!")
#         receipt.append("=" * 40)
        
#         self.receipt_text.setText("\n".join(receipt))
        
#         # Store data for printing/PDF
#         self.sale = sale
#         self.items = items
#         self.receipt_lines = receipt
    
#    # views/receipt_view.py - print_receipt metodini tuzatamiz
# def print_receipt(self):
#     try:
#         # Print using system printer
#         from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
#         from PyQt6.QtGui import QPainter, QFont
        
#         printer = QPrinter(QPrinter.PrinterMode.HighResolution)
#         printer.setPageSize(QPrinter.PageSize.A6)
        
#         print_dialog = QPrintDialog(printer, self)
#         if print_dialog.exec() == QDialog.DialogCode.Accepted:
#             painter = QPainter(printer)
#             painter.setFont(QFont("Courier", 8))
            
#             y = 20
#             for line in self.receipt_lines:
#                 painter.drawText(20, y, line)
#                 y += 15
            
#             painter.end()
            
#     except Exception as e:
#         QMessageBox.warning(self, "Xatolik", f"Chop etishda xatolik: {str(e)}")
    
#     def save_pdf(self):
#         try:
#             file_path, _ = QFileDialog.getSaveFileName(
#                 self, "PDF faylni saqlash", f"chek_{self.sale_id}.pdf", "PDF Files (*.pdf)"
#             )
#             if not file_path:
#                 return
            
#             # Create PDF
#             doc = SimpleDocTemplate(file_path, pagesize=A6)
#             styles = getSampleStyleSheet()
#             story = []
            
#             # Add receipt content
#             for line in self.receipt_lines:
#                 paragraph = Paragraph(line.replace(' ', '&nbsp;'), styles['Normal'])
#                 story.append(paragraph)
#                 story.append(Spacer(1, 5))
            
#             doc.build(story)
#             QMessageBox.information(self, "Muvaffaqiyat", "PDF fayl saqlandi!")
            
#         except Exception as e:
#             QMessageBox.critical(self, "Xatolik", f"PDF saqlashda xatolik: {str(e)}")


# views/receipt_view.py
# views/receipt_view.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from utils.styles import DARK_STYLE
from controllers.sale_controller import SaleController
from controllers.product_controller import ProductController
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A6
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

class ReceiptDialog(QDialog):
    def __init__(self, sale_id, parent=None, payment_type="Naxt"):
        super().__init__(parent)
        self.sale_id = sale_id
        self.payment_type = payment_type
        self.sale_controller = SaleController()
        self.product_controller = ProductController()
        self.receipt_lines = []
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.load_receipt_data()
    
    def setup_ui(self):
        self.setWindowTitle("🧾 Chek")
        self.setFixedSize(420, 650)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("🧾 SOTUV CHEKI")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #6c63ff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.receipt_text = QTextEdit()
        self.receipt_text.setReadOnly(True)
        self.receipt_text.setFont(QFont("Courier New", 10))
        self.receipt_text.setStyleSheet("""
            QTextEdit {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 12px;
                padding: 15px;
                color: #e0e0e0;
            }
        """)
        layout.addWidget(self.receipt_text)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        print_btn = QPushButton("🖨️ Chop etish")
        print_btn.setObjectName("primaryButton")
        print_btn.setMinimumHeight(45)
        print_btn.clicked.connect(self.print_receipt)
        button_layout.addWidget(print_btn)
        
        pdf_btn = QPushButton("📄 PDF saqlash")
        pdf_btn.setObjectName("primaryButton")
        pdf_btn.setMinimumHeight(45)
        pdf_btn.clicked.connect(self.save_pdf)
        button_layout.addWidget(pdf_btn)
        
        close_btn = QPushButton("❌ Yopish")
        close_btn.setObjectName("dangerButton")
        close_btn.setMinimumHeight(45)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def load_receipt_data(self):
        try:
            sale = self.sale_controller.get_sale_by_id(self.sale_id)
            if not sale:
                self.receipt_text.setText("Chek ma'lumotlari topilmadi!")
                return
            
            items = self.sale_controller.get_sale_items(self.sale_id)
            
            receipt = []
            receipt.append("=" * 42)
            receipt.append("        🏪 POS TIZIMI")
            receipt.append("        Moy almashtirish")
            receipt.append("=" * 42)
            receipt.append("")
            
            created_at = sale.get('created_at', '')
            receipt.append(f"Sana: {created_at}")
            receipt.append(f"Chek №: {sale.get('id', 0):06d}")
            receipt.append(f"💳 To'lov: {self.payment_type}")
            receipt.append("")
            
            # Car information
            receipt.append("-" * 42)
            receipt.append("🚗 AVTOMOBIL MA'LUMOTLARI")
            receipt.append(f"Raqam: {sale.get('car_number', '-')}")
            receipt.append(f"Model: {sale.get('car_model', '-')}")
            receipt.append(f"📱 Telefon: {sale.get('phone_number', '-')}")
            receipt.append(f"Joriy km: {sale.get('current_km', 0):,.0f} km")
            receipt.append(f"Keyingi moy: {sale.get('next_km', 0):,.0f} km")
            receipt.append(f"Moy almashtirilgan: {sale.get('oil_change_date', '-')}")
            receipt.append(f"Keyingi almashtirish: {sale.get('next_oil_change_date', '-')}")
            receipt.append("-" * 42)
            receipt.append("")
            
            receipt.append("-" * 42)
            receipt.append(f"{'Mahsulot':<20} {'Narx':>8} {'Miq':>5} {'Jami':>10}")
            receipt.append("-" * 42)
            
            for item in items:
                name = item.get('product_name', '')[:18]
                if len(item.get('product_name', '')) > 18:
                    name += ".."
                
                receipt.append(
                    f"{name:<20} "
                    f"{item.get('sell_price', 0):>8.0f} "
                    f"{item.get('quantity', 0):>5.1f} "
                    f"{item.get('subtotal', 0):>10.0f}"
                )
            
            receipt.append("-" * 42)
            receipt.append(f"{'Jami:':<34} {sale.get('total_amount', 0):>10.0f}")
            
            if sale.get('discount', 0) > 0:
                receipt.append(f"{'Chegirma:':<34} {sale.get('discount', 0):>10.0f}%")
                receipt.append(f"{'Yakuniy:':<34} {sale.get('total_amount', 0):>10.0f}")
            
            receipt.append("")
            receipt.append("=" * 42)
            receipt.append("     Rahmat! Xush kelibsiz!")
            receipt.append("=" * 42)
            
            self.receipt_text.setText("\n".join(receipt))
            
            # Store data for printing/PDF
            self.sale = sale
            self.items = items
            self.receipt_lines = receipt
            
        except Exception as e:
            print(f"Error loading receipt: {e}")
            self.receipt_text.setText(f"Xatolik: {str(e)}")
    
    def print_receipt(self):
        try:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setPageSize(QPrinter.PageSize.A6)
            printer.setPageMargins(10, 10, 10, 10, QPrinter.Unit.Millimeter)
            
            print_dialog = QPrintDialog(printer, self)
            if print_dialog.exec() == QDialog.DialogCode.Accepted:
                painter = QPainter(printer)
                painter.setFont(QFont("Courier New", 8))
                
                y = 20
                x = 20
                line_height = 14
                
                for line in self.receipt_lines:
                    painter.drawText(x, y, line)
                    y += line_height
                    if y > printer.height() - 50:
                        printer.newPage()
                        y = 20
                
                painter.end()
                QMessageBox.information(self, "Muvaffaqiyat", "Chek chop etildi!")
                
        except Exception as e:
            QMessageBox.warning(self, "Xatolik", f"Chop etishda xatolik: {str(e)}")
    
    def save_pdf(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "PDF faylni saqlash", f"chek_{self.sale_id}.pdf", "PDF Files (*.pdf)"
            )
            if not file_path:
                return
            
            doc = SimpleDocTemplate(file_path, pagesize=A6)
            styles = getSampleStyleSheet()
            story = []
            
            for line in self.receipt_lines:
                paragraph = Paragraph(line.replace(' ', '&nbsp;'), styles['Normal'])
                story.append(paragraph)
                story.append(Spacer(1, 4))
            
            doc.build(story)
            QMessageBox.information(self, "Muvaffaqiyat", "PDF fayl saqlandi!")
            
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"PDF saqlashda xatolik: {str(e)}")