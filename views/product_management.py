# views/product_management.py - TO'LIQ TUZATILGAN (1721 QATOR)
# ============================================================

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils.styles import DARK_STYLE
from controllers.product_controller import ProductController
from controllers.firm_controller import FirmController
from controllers.category_controller import CategoryController
from models.models import Product
from models.repositories import PurchaseRepository
from utils.currency import get_usd_rate
import os
import time
import re


# ============================================================
# TUZATILGAN: CommaDoubleSpinBox - vergul va nuqta bilan ishlash
# ============================================================
class CommaDoubleSpinBox(QDoubleSpinBox):
    """Oddiy QDoubleSpinBox, lekin klaviaturada '.' bosilsa ham, ',' bosilsa ham
    ikkalasi bir xil o'nlik ajratuvchi sifatida qabul qilinadi (masalan 2.8 yoki 2,8)."""
    
    def keyPressEvent(self, event):
        if event.text() == '.':
            comma_event = QKeyEvent(
                event.type(), Qt.Key.Key_Comma, event.modifiers(), ','
            )
            super().keyPressEvent(comma_event)
            return
        super().keyPressEvent(event)
    
    def valueFromText(self, text):
        """Vergulni nuqtaga almashtirish (parse qilish uchun)"""
        text = text.replace(',', '.')
        return super().valueFromText(text)
    
    def textFromValue(self, value):
        """Nuqtani vergulga almashtirish (ko'rinish uchun)"""
        text = super().textFromValue(value)
        return text.replace('.', ',')


# ============================================================
# Kategoriyalar ro'yxati (guruhlangan)
# ============================================================
CATEGORIES = {
    "🛢️ Moylar": [
        "Moy",
    ],
    "🧰 Filterlar": [
        "Havo filter",
        "Salon filter",
        "Moy filter",
        "Korobka filter",
    ],
    "⚙️ Boshqa": [
        "Reduktor",
    ],
}

CUSTOM_CATEGORY_TEXT = "✍️ Boshqa (qo'lda yozish)..."

def create_grouped_category_combo():
    combo = QComboBox()
    combo.setMinimumHeight(40)
    model = QStandardItemModel()

    empty_item = QStandardItem("— Kategoriya tanlang —")
    empty_item.setData("", Qt.ItemDataRole.UserRole)
    model.appendRow(empty_item)

    for group_name, sub_items in CATEGORIES.items():
        header_item = QStandardItem(group_name)
        header_item.setFlags(header_item.flags() & ~Qt.ItemFlag.ItemIsEnabled & ~Qt.ItemFlag.ItemIsSelectable)
        font = header_item.font()
        font.setBold(True)
        header_item.setFont(font)
        model.appendRow(header_item)

        for sub_name in sub_items:
            sub_item = QStandardItem("     " + sub_name)
            sub_item.setData(sub_name, Qt.ItemDataRole.UserRole)
            model.appendRow(sub_item)

    custom_item = QStandardItem(CUSTOM_CATEGORY_TEXT)
    custom_item.setData(CUSTOM_CATEGORY_TEXT, Qt.ItemDataRole.UserRole)
    model.appendRow(custom_item)

    combo.setModel(model)
    combo.setStyleSheet("""
        QComboBox {
            background: #14142a;
            border: 2px solid #2a2a4a;
            border-radius: 8px;
            padding: 8px 12px;
            color: #e0e0e0;
            font-size: 14px;
        }
        QComboBox:focus {
            border: 2px solid #6c63ff;
        }
        QComboBox::drop-down {
            border: none;
        }
    """)
    return combo

def set_category_combo_value(combo, value):
    if not value:
        combo.setCurrentIndex(0)
        return
    for i in range(combo.count()):
        if combo.itemData(i, Qt.ItemDataRole.UserRole) == value:
            combo.setCurrentIndex(i)
            return
    item = QStandardItem("     " + value)
    item.setData(value, Qt.ItemDataRole.UserRole)
    model = combo.model()
    model.insertRow(model.rowCount() - 1, item)
    combo.setCurrentIndex(model.rowCount() - 2)


# ============================================================
# DRAG & DROP UCHUN LIST WIDGETLAR
# ============================================================
class ProductListWidget(QListWidget):
    """Mahsulotlar ro'yxati - Drag bilan mahsulotlarni tashish uchun"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.setStyleSheet("""
            QListWidget {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 6px 10px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background: #4a4a8a;
                color: white;
            }
            QListWidget::item:hover {
                background: #2a2a4a;
            }
        """)
    
    def startDrag(self, actions):
        """Drag boshlanganda mahsulot ID'larini MIME data sifatida yuborish"""
        from PyQt6.QtCore import QMimeData
        from PyQt6.QtGui import QDrag
        
        selected_items = self.selectedItems()
        if not selected_items:
            return
        
        ids = [str(item.data(Qt.ItemDataRole.UserRole)) for item in selected_items]
        
        mime_data = QMimeData()
        mime_data.setText(','.join(ids))
        
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.CopyAction)


class CategoryDropListWidget(QListWidget):
    """Kategoriyalar ro'yxati - Drop orqali mahsulotlarni qabul qilish uchun"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.setStyleSheet("""
            QListWidget {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 6px 10px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background: #4a4a8a;
                color: white;
            }
            QListWidget::item:hover {
                background: #2a2a4a;
            }
        """)
    
    def dragEnterEvent(self, event):
        """Drag kirganda qabul qilish"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Drop bo'lganda mahsulotlarni kategoriyaga biriktirish"""
        item = self.itemAt(event.position().toPoint())
        if item:
            category_id = item.data(Qt.ItemDataRole.UserRole)
            product_ids_text = event.mimeData().text()
            
            if product_ids_text:
                product_ids = [int(pid.strip()) for pid in product_ids_text.split(',') if pid.strip()]
                
                if product_ids:
                    category_controller = CategoryController()
                    result = category_controller.assign_products(product_ids, category_id)
                    
                    if result:
                        parent_widget = self.parent()
                        if parent_widget and hasattr(parent_widget, 'load_products'):
                            parent_widget.load_products()
                        if parent_widget and hasattr(parent_widget, 'load_categories'):
                            parent_widget.load_categories()
                        QMessageBox.information(
                            self, 
                            "Muvaffaqiyat", 
                            f"✅ {len(product_ids)} ta mahsulot kategoriyaga biriktirildi!"
                        )
                    else:
                        QMessageBox.warning(
                            self, 
                            "Xatolik", 
                            "Mahsulotlarni kategoriyaga biriktirishda xatolik!"
                        )
        event.acceptProposedAction()


class ProductManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.product_controller = ProductController()
        self.selected_category_id = "ALL"
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.load_products()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        title = QLabel("📦 Mahsulotlar")
        title.setObjectName("titleLabel")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Mahsulot qidirish...")
        self.search_input.setMaximumWidth(300)
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 10px;
                padding: 10px 15px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        self.search_input.textChanged.connect(self.search_products)
        header_layout.addWidget(self.search_input)
        
        add_btn = QPushButton("➕ Yangi mahsulot")
        add_btn.setObjectName("primaryButton")
        add_btn.setMinimumHeight(40)
        add_btn.clicked.connect(self.show_add_product_dialog)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        category_panel = QWidget()
        category_panel.setStyleSheet("""
            QWidget {
                background: #14142a;
                border-radius: 10px;
                border: 2px solid #2a2a4a;
            }
        """)
        category_layout = QVBoxLayout(category_panel)
        category_layout.setContentsMargins(10, 10, 10, 10)
        category_layout.setSpacing(8)
        
        category_header_layout = QHBoxLayout()
        
        category_title = QLabel("📂 Kategoriyalar")
        category_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #a0a0b8; padding: 5px;")
        category_header_layout.addWidget(category_title)
        
        category_header_layout.addStretch()
        
        add_category_btn = QPushButton("➕ YANGI")
        add_category_btn.setFixedSize(80, 32)
        add_category_btn.setToolTip("Yangi kategoriya (papka) qo'shish")
        add_category_btn.setStyleSheet("""
            QPushButton {
                background: #6c63ff;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 0 10px;
            }
            QPushButton:hover {
                background: #5a52d5;
            }
            QPushButton:pressed {
                background: #4a42b5;
            }
        """)
        add_category_btn.clicked.connect(self.add_category)
        category_header_layout.addWidget(add_category_btn)
        
        category_layout.addLayout(category_header_layout)
        
        category_label = QLabel("Mahsulotni kategoriyaga tashlang (Drag & Drop)")
        category_label.setWordWrap(True)
        category_label.setStyleSheet("color: #6a6a8a; font-size: 12px; padding: 5px;")
        category_layout.addWidget(category_label)
        
        self.category_list = CategoryDropListWidget(self)
        self.category_list.itemClicked.connect(self.on_category_selected)
        category_layout.addWidget(self.category_list)
        
        cat_btn_layout = QHBoxLayout()
        delete_cat_btn = QPushButton("🗑️ Kategoriyani o'chirish")
        delete_cat_btn.setObjectName("dangerButton")
        delete_cat_btn.setMinimumHeight(35)
        delete_cat_btn.clicked.connect(self.delete_selected_category)
        cat_btn_layout.addWidget(delete_cat_btn)
        category_layout.addLayout(cat_btn_layout)
        
        self.load_categories()
        
        main_splitter.addWidget(category_panel)
        
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(10)

        self.filter_label = QLabel("")
        self.filter_label.setStyleSheet("color: #6c63ff; font-size: 13px; font-weight: bold;")
        self.filter_label.setVisible(False)
        table_layout.addWidget(self.filter_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            '', 'ID', 'Nomi', 'Kategoriya', 'Tannarx (so\'m)', 
            'Sotuv narxi (so\'m)', 'Miqdor', 'Jami tannarx', 'Jami sotuv', 'Izoh'
        ])
        self.table.setColumnWidth(0, 30)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
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
        self.table.verticalHeader().setDefaultSectionSize(60)
        table_layout.addWidget(self.table)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        edit_btn = QPushButton("✏️ Tahrirlash")
        edit_btn.setObjectName("primaryButton")
        edit_btn.clicked.connect(self.edit_product)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ O'chirish")
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(self.delete_product)
        button_layout.addWidget(delete_btn)

        move_btn = QPushButton("📂 Tanlanganlarni ko'chirish")
        move_btn.setObjectName("secondaryButton")
        move_btn.clicked.connect(self.move_selected_products_to_category)
        button_layout.addWidget(move_btn)
        
        refresh_btn = QPushButton("🔄 Yangilash")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.clicked.connect(self.load_products)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        table_layout.addLayout(button_layout)
        
        main_splitter.addWidget(table_widget)
        
        main_splitter.setSizes([250, 650])
        
        layout.addWidget(main_splitter)
    
    def load_categories(self):
        """Kategoriyalarni ro'yxatga yuklash"""
        try:
            category_controller = CategoryController()
            categories = category_controller.get_all()
            
            self.category_list.clear()
            
            all_item = QListWidgetItem("📦 Barcha mahsulotlar")
            all_item.setData(Qt.ItemDataRole.UserRole, "ALL")
            self.category_list.addItem(all_item)

            none_item = QListWidgetItem("❔ Kategoriyasiz")
            none_item.setData(Qt.ItemDataRole.UserRole, None)
            self.category_list.addItem(none_item)
            
            for cat in categories:
                count = category_controller.get_category_product_count(cat['id'])
                item = QListWidgetItem(f"{cat.get('icon') or '📁'} {cat['name']}  ({count})")
                item.setData(Qt.ItemDataRole.UserRole, cat['id'])
                self.category_list.addItem(item)

            category_controller.close()
                
        except Exception as e:
            print(f"❌ Kategoriyalarni yuklashda xatolik: {e}")

    def add_category(self):
        name, ok = QInputDialog.getText(self, "➕ Yangi kategoriya", "Kategoriya (papka) nomini kiriting:")
        name = name.strip() if name else ""
        if not ok or not name:
            return

        category_controller = CategoryController()
        new_id = category_controller.create(name)
        category_controller.close()

        if new_id:
            QMessageBox.information(self, "Muvaffaqiyat", f"✅ '{name}' papkasi yaratildi!")
            self.load_categories()
        else:
            QMessageBox.warning(self, "Xatolik", "Bu nomdagi kategoriya allaqachon mavjud yoki xatolik yuz berdi!")

    def delete_selected_category(self):
        current_item = self.category_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ogohlantirish", "Iltimos, o'chirish uchun papka (kategoriya) tanlang!")
            return
        
        category_id = current_item.data(Qt.ItemDataRole.UserRole)
        if category_id in ("ALL", None):
            QMessageBox.warning(self, "Ogohlantirish", "Bu papkani o'chirib bo'lmaydi! (Bu tizim bo'limi)")
            return

        category_name = current_item.text().split("  (")[0]
        reply = QMessageBox.question(
            self, "Tasdiqlash",
            f"'{category_name}' papkasini (kategoriyani) o'chirmoqchimisiz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            category_controller = CategoryController()
            result = category_controller.delete(category_id)
            category_controller.close()
            
            if result:
                QMessageBox.information(self, "Muvaffaqiyat", f"✅ '{category_name}' papkasi o'chirildi!")
                self.load_categories()
                self.load_products()
                if self.parent() and hasattr(self.parent(), 'pos_view'):
                    self.parent().pos_view.load_products()
            else:
                QMessageBox.warning(self, "Xatolik", "Papkani o'chirishda xatolik!")
    
    def move_selected_products_to_category(self):
        selected_ids = []
        for row in range(self.table.rowCount()):
            checkbox_item = self.table.item(row, 0)
            if checkbox_item and checkbox_item.checkState() == Qt.CheckState.Checked:
                product_id = int(self.table.item(row, 1).text())
                selected_ids.append(product_id)

        if not selected_ids:
            QMessageBox.warning(self, "Ogohlantirish", "Iltimos, avval jadvaldan mahsulotlarni belgilang (Checkbox bilan)!")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("📂 Papkaga ko'chirish")
        dialog.setFixedSize(350, 150)
        dialog.setStyleSheet(DARK_STYLE)
        layout = QVBoxLayout(dialog)
        
        label = QLabel(f"Tanlangan {len(selected_ids)} ta mahsulotni qaysi papkaga ko'chirilsin?")
        layout.addWidget(label)
        
        combo = QComboBox()
        combo.setMinimumHeight(40)
        category_controller = CategoryController()
        categories = category_controller.get_all()
        for cat in categories:
            combo.addItem(f"{cat.get('icon') or '📁'} {cat['name']}", cat['id'])
        category_controller.close()
        layout.addWidget(combo)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Ko'chirish")
        ok_btn.setObjectName("primaryButton")
        cancel_btn = QPushButton("Bekor qilish")
        cancel_btn.setObjectName("dangerButton")
        cancel_btn.clicked.connect(dialog.reject)
        
        def on_ok():
            target_category_id = combo.currentData()
            if target_category_id is None:
                QMessageBox.warning(dialog, "Xatolik", "Papka tanlanmadi!")
                return
            dialog.accept()
            
            controller = CategoryController()
            result = controller.assign_products(selected_ids, target_category_id)
            controller.close()
            
            if result:
                QMessageBox.information(self, "Muvaffaqiyat", f"✅ {len(selected_ids)} ta mahsulot ko'chirildi!")
                self.load_products()
                self.load_categories()
                if self.parent() and hasattr(self.parent(), 'pos_view'):
                    self.parent().pos_view.load_products()
            else:
                QMessageBox.warning(self, "Xatolik", "Mahsulotlarni ko'chirishda xatolik!")
        
        ok_btn.clicked.connect(on_ok)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec()

    def on_category_selected(self, item):
        category_id = item.data(Qt.ItemDataRole.UserRole)
        self.selected_category_id = category_id
        self.search_input.clear()

        if category_id == "ALL":
            self.filter_label.setVisible(False)
        else:
            self.filter_label.setText(f"🔎 Filtr: {item.text().strip()}  —  tozalash uchun 'Barcha mahsulotlar'ni bosing")
            self.filter_label.setVisible(True)

        self.load_products()
    
    def load_products(self, search_term=""):
        try:
            if self.selected_category_id not in ("ALL", None) and not search_term:
                category_controller = CategoryController()
                products = category_controller.get_products_by_category(self.selected_category_id)
                category_controller.close()
            elif self.selected_category_id is None and not search_term:
                # "Kategoriyasiz" - show products with no category
                all_products = self.product_controller.get_all_products("")
                products = [p for p in all_products if not p.get('category') and not p.get('category_id')]
            else:
                products = self.product_controller.get_all_products(search_term)

            self.table.setRowCount(len(products))
            
            for i, product in enumerate(products):
                chk_item = QTableWidgetItem()
                chk_item.setCheckState(Qt.CheckState.Unchecked)
                self.table.setItem(i, 0, chk_item)
                
                self.table.setItem(i, 1, QTableWidgetItem(str(product['id'])))
                self.table.setItem(i, 2, QTableWidgetItem(product['name']))
                self.table.setItem(i, 3, QTableWidgetItem(product.get('category', '')))
                self.table.setItem(i, 4, QTableWidgetItem(f"{product['cost_price']:,.2f}"))
                self.table.setItem(i, 5, QTableWidgetItem(f"{product['sell_price']:,.2f}"))
                self.table.setItem(i, 6, QTableWidgetItem(f"{product['quantity']} {product.get('unit', 'dona')}"))
                
                total_cost = product['cost_price'] * product['quantity']
                self.table.setItem(i, 7, QTableWidgetItem(f"{total_cost:,.2f}"))
                
                total_value = product['sell_price'] * product['quantity']
                self.table.setItem(i, 8, QTableWidgetItem(f"{total_value:,.2f}"))
                
                self.table.setItem(i, 9, QTableWidgetItem(product.get('note', '')))
            
            self.table.resizeColumnsToContents()
        except Exception as e:
            print(f"Error loading products: {e}")
    
    def search_products(self):
        search_term = self.search_input.text()
        if search_term:
            self.selected_category_id = "ALL"
            self.filter_label.setVisible(False)
        self.load_products(search_term)
    
    def show_add_product_dialog(self):
        dialog = ProductDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
            self.load_categories()
            if self.parent() and hasattr(self.parent(), 'pos_view'):
                self.parent().pos_view.load_products()
    
    def edit_product(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ogohlantirish", "Iltimos, tahrirlash uchun mahsulot tanlang!")
            return
        
        product_id = int(self.table.item(selected, 1).text())
        product_data = self.product_controller.get_product_by_id(product_id)
        if product_data:
            dialog = ProductDialog(self, product_data)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_products()
                self.load_categories()
                if self.parent() and hasattr(self.parent(), 'pos_view'):
                    self.parent().pos_view.load_products()
    
    def delete_product(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ogohlantirish", "Iltimos, o'chirish uchun mahsulot tanlang!")
            return
        
        product_name = self.table.item(selected, 2).text()
        reply = QMessageBox.question(
            self, "Tasdiqlash",
            f"'{product_name}' mahsulotini o'chirmoqchimisiz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            product_id = int(self.table.item(selected, 1).text())
            result = self.product_controller.delete_product(product_id)
            if result:
                self.load_products()
                self.load_categories()
                if self.parent() and hasattr(self.parent(), 'pos_view'):
                    self.parent().pos_view.load_products()
                QMessageBox.information(self, "Muvaffaqiyat", "✅ Mahsulot o'chirildi!")
            else:
                QMessageBox.warning(self, "Xatolik", "Mahsulotni o'chirishda xatolik!")


class ProductDialog(QDialog):
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
        self.product_data = product_data
        self.product_controller = ProductController()
        self.firm_controller = FirmController()
        self._updating = False
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.load_data()
        self.load_firms()
        self.auto_rate_checkbox.setChecked(not bool(self.product_data))
    
    def setup_ui(self):
        self.setWindowTitle("Yangi mahsulot" if not self.product_data else "Mahsulotni tahrirlash")
        self.setFixedSize(620, 950)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        form_layout = QFormLayout(scroll_widget)
        form_layout.setSpacing(15)
        form_layout.setVerticalSpacing(15)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Mahsulot nomi")
        self.name_input.setMinimumHeight(40)
        self.name_input.setStyleSheet("""
            QLineEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 10px 15px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        form_layout.addRow("Nomi:", self.name_input)
        
        self.category_input = create_grouped_category_combo()
        self.category_input.currentIndexChanged.connect(self.on_category_changed)
        form_layout.addRow("Kategoriya:", self.category_input)

        # ============================================================
        # PAPKA (BO'LIM) TANLASH - "Mahsulotlar" bo'limidagi chap paneldagi
        # papkalar (kategoriyalar) shu yerdan tanlanadi
        # ============================================================
        self.folder_input = QComboBox()
        self.folder_input.setMinimumHeight(40)
        self.folder_input.setStyleSheet("""
            QComboBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QComboBox:focus {
                border: 2px solid #6c63ff;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self._load_folders()
        form_layout.addRow("📂 Papka:", self.folder_input)
        
        currency_group = QGroupBox("💱 Valyuta va kurs")
        currency_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #2a2a4a;
                border-radius: 10px;
                margin-top: 5px;
                padding-top: 14px;
                background: #14142a;
            }
            QGroupBox::title {
                color: #a0a0b8;
                font-weight: bold;
                padding: 0 10px;
            }
        """)
        currency_layout = QFormLayout(currency_group)
        currency_layout.setSpacing(12)
        
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["💵 Dollar ($)", "💰 So'm (so'm)"])
        self.currency_combo.setMinimumHeight(35)
        self.currency_combo.setStyleSheet("""
            QComboBox {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
                font-weight: 600;
            }
            QComboBox:focus { border: 2px solid #6c63ff; }
            QComboBox::drop-down { border: none; }
        """)
        currency_layout.addRow("Valyuta:", self.currency_combo)
        
        auto_toggle_widget = QWidget()
        auto_toggle_layout = QHBoxLayout(auto_toggle_widget)
        auto_toggle_layout.setContentsMargins(0, 0, 0, 0)
        auto_toggle_layout.setSpacing(8)
        
        self.auto_rate_checkbox = QCheckBox("🔄 Avtomatik (CBU.uz rasmiy kursi)")
        self.auto_rate_checkbox.setStyleSheet("""
            QCheckBox {
                color: #a0a0b8;
                font-size: 13px;
                font-weight: 600;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 36px;
                height: 20px;
                border-radius: 10px;
                background: #2a2a4a;
                border: 2px solid #3a3a5a;
            }
            QCheckBox::indicator:checked {
                background: #00c853;
                border: 2px solid #00c853;
            }
        """)
        self.auto_rate_checkbox.toggled.connect(self.on_auto_rate_toggled)
        auto_toggle_layout.addWidget(self.auto_rate_checkbox)
        auto_toggle_layout.addStretch()
        currency_layout.addRow("", auto_toggle_widget)
        
        rate_widget = QWidget()
        rate_layout = QHBoxLayout(rate_widget)
        rate_layout.setContentsMargins(0, 0, 0, 0)
        rate_layout.setSpacing(8)
        
        self.exchange_rate_input = CommaDoubleSpinBox()
        self.exchange_rate_input.setRange(0, 20000)
        self.exchange_rate_input.setPrefix("1$ = ")
        self.exchange_rate_input.setSuffix(" so'm")
        self.exchange_rate_input.setValue(12600)
        self.exchange_rate_input.setMinimumHeight(35)
        self.exchange_rate_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #6c63ff;
            }
            QDoubleSpinBox:disabled {
                color: #6a6a8a;
                background: #101022;
            }
        """)
        self.exchange_rate_input.valueChanged.connect(self.on_rate_changed)
        rate_layout.addWidget(self.exchange_rate_input, 1)
        
        self.auto_rate_btn = QPushButton("🔄 Auto")
        self.auto_rate_btn.setObjectName("primaryButton")
        self.auto_rate_btn.setFixedSize(60, 35)
        self.auto_rate_btn.setToolTip("Hozirgi kursni avtomatik olish")
        self.auto_rate_btn.clicked.connect(self.load_current_rate)
        rate_layout.addWidget(self.auto_rate_btn)
        
        currency_layout.addRow("Kurs:", rate_widget)
        form_layout.addRow(currency_group)
        
        prices_group = QGroupBox("💰 Narxlar")
        prices_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #2a2a4a;
                border-radius: 10px;
                margin-top: 5px;
                padding-top: 14px;
                background: #14142a;
            }
            QGroupBox::title {
                color: #a0a0b8;
                font-weight: bold;
                padding: 0 10px;
            }
        """)
        prices_layout = QFormLayout(prices_group)
        prices_layout.setSpacing(12)
        
        self.cost_price_input = CommaDoubleSpinBox()
        self.cost_price_input.setRange(0, 1000000000)
        self.cost_price_input.setPrefix("so'm ")
        self.cost_price_input.setMinimumHeight(40)
        self.cost_price_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #6c63ff;
            }
        """)
        self.cost_price_input.valueChanged.connect(self.on_cost_price_changed)
        prices_layout.addRow("Tannarx (so'm):", self.cost_price_input)
        
        # ===== TUZATILGAN: dollar_cost_input ga setSingleStep(0.01) qo'shildi =====
        self.dollar_cost_input = CommaDoubleSpinBox()
        self.dollar_cost_input.setRange(0, 1000000)
        self.dollar_cost_input.setSingleStep(0.01)
        self.dollar_cost_input.setPrefix("$ ")
        self.dollar_cost_input.setMinimumHeight(40)
        self.dollar_cost_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #6c63ff;
            }
        """)
        self.dollar_cost_input.valueChanged.connect(self.on_dollar_cost_changed)
        prices_layout.addRow("Tannarx ($):", self.dollar_cost_input)
        
        self.sell_price_input = CommaDoubleSpinBox()
        self.sell_price_input.setRange(0, 1000000000)
        self.sell_price_input.setPrefix("so'm ")
        self.sell_price_input.setMinimumHeight(40)
        self.sell_price_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #6c63ff;
            }
        """)
        self.sell_price_input.valueChanged.connect(self.on_sell_price_changed)
        prices_layout.addRow("Sotuv narxi (so'm):", self.sell_price_input)
        
        # ===== TUZATILGAN: dollar_sell_input ga setSingleStep(0.01) qo'shildi =====
        self.dollar_sell_input = CommaDoubleSpinBox()
        self.dollar_sell_input.setRange(0, 1000000)
        self.dollar_sell_input.setSingleStep(0.01)
        self.dollar_sell_input.setPrefix("$ ")
        self.dollar_sell_input.setMinimumHeight(40)
        self.dollar_sell_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #6c63ff;
            }
        """)
        self.dollar_sell_input.valueChanged.connect(self.on_dollar_sell_changed)
        prices_layout.addRow("Sotuv narxi ($):", self.dollar_sell_input)
        
        form_layout.addRow(prices_group)
        
        self.quantity_input = CommaDoubleSpinBox()
        self.quantity_input.setRange(0, 1000000)
        self.quantity_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #6c63ff;
            }
        """)
        self.quantity_input.valueChanged.connect(self.update_purchase_preview)
        form_layout.addRow("Miqdor:", self.quantity_input)
        
        self.unit_input = QComboBox()
        self.unit_input.addItems(['dona', 'litr', 'kg', 'metr', 'dasta'])
        self.unit_input.setStyleSheet("""
            QComboBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QComboBox:focus {
                border: 2px solid #6c63ff;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        form_layout.addRow("O'lchov birligi:", self.unit_input)
        
        self.min_quantity_input = CommaDoubleSpinBox()
        self.min_quantity_input.setRange(0, 1000)
        self.min_quantity_input.setValue(5)
        self.min_quantity_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #6c63ff;
            }
        """)
        form_layout.addRow("Minimal qoldiq:", self.min_quantity_input)
        
        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(80)
        self.note_input.setPlaceholderText("Qo'shimcha ma'lumot...")
        self.note_input.setStyleSheet("""
            QTextEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 10px 15px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        form_layout.addRow("Izoh:", self.note_input)
        
        purchase_group = QGroupBox("🧾 Xarid to'lovi (ombordan kirim)")
        purchase_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #2a2a4a;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 14px;
                background: #14142a;
            }
            QGroupBox::title {
                color: #a0a0b8;
                font-weight: bold;
                padding: 0 10px;
            }
        """)
        purchase_layout = QFormLayout(purchase_group)
        purchase_layout.setSpacing(12)

        self.payment_type_combo = QComboBox()
        self.payment_type_combo.addItems(["💵 Naxtga oldim", "📝 Nasiyaga oldim"])
        self.payment_type_combo.setStyleSheet("""
            QComboBox {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
                font-weight: 600;
            }
            QComboBox:focus { border: 2px solid #6c63ff; }
        """)
        self.payment_type_combo.currentTextChanged.connect(self.on_purchase_payment_changed)
        purchase_layout.addRow("To'lov turi:", self.payment_type_combo)

        purchase_date_label = QLabel("Xarid sanasi:")
        purchase_date_label.setStyleSheet("color: #a0a0b8; font-size: 14px;")
        
        self.purchase_date_input = QDateEdit()
        self.purchase_date_input.setDate(QDate.currentDate())
        self.purchase_date_input.setCalendarPopup(True)
        self.purchase_date_input.setDisplayFormat("dd.MM.yyyy")
        self.purchase_date_input.setStyleSheet("""
            QDateEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QDateEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        purchase_layout.addRow(purchase_date_label, self.purchase_date_input)

        due_date_label = QLabel("📅 To'lov muddati:")
        due_date_label.setStyleSheet("color: #a0a0b8; font-size: 14px;")
        
        self.due_date_input = QDateEdit()
        self.due_date_input.setDate(QDate.currentDate().addMonths(1))
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDisplayFormat("dd.MM.yyyy")
        self.due_date_input.setStyleSheet("""
            QDateEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QDateEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        purchase_layout.addRow(due_date_label, self.due_date_input)

        self.due_date_input.setVisible(False)
        due_date_label.setVisible(False)

        self.purchase_hint_label = QLabel(
            "Miqdorni ko'paytirsangiz, qo'shilgan qism yetkazib beruvchidan\n"
            "shu to'lov turi bilan olingan deb qayd etiladi."
        )
        self.purchase_hint_label.setWordWrap(True)
        self.purchase_hint_label.setStyleSheet("color: #6a6a8a; font-size: 12px; background: transparent;")
        purchase_layout.addRow(self.purchase_hint_label)

        form_layout.addRow(purchase_group)
        
        firm_group = QGroupBox("🏢 Firma (Nasiyaga olinganda)")
        firm_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #f59e0b;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 14px;
                background: #14142a;
            }
            QGroupBox::title {
                color: #f59e0b;
                font-weight: bold;
                padding: 0 10px;
            }
        """)
        firm_layout = QVBoxLayout(firm_group)
        firm_layout.setSpacing(8)
        firm_layout.setContentsMargins(15, 10, 15, 15)
        
        firm_select_layout = QHBoxLayout()
        firm_select_layout.setSpacing(8)
        
        self.firm_combo = QComboBox()
        self.firm_combo.setMinimumHeight(35)
        self.firm_combo.setStyleSheet("""
            QComboBox {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QComboBox:focus {
                border: 2px solid #f59e0b;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #1a1a2e;
                color: #e0e0e0;
                selection-background-color: #4a4a8a;
                padding: 4px;
            }
        """)
        firm_select_layout.addWidget(self.firm_combo, 1)
        
        new_firm_btn = QPushButton("➕")
        new_firm_btn.setFixedSize(35, 35)
        new_firm_btn.setToolTip("Yangi firma qo'shish")
        new_firm_btn.setStyleSheet("""
            QPushButton {
                background: #6c63ff;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #5a52d5;
            }
        """)
        new_firm_btn.clicked.connect(self.show_add_firm_dialog)
        firm_select_layout.addWidget(new_firm_btn)
        
        firm_layout.addLayout(firm_select_layout)
        
        self.firm_info_label = QLabel("💡 Firma tanlanmagan. Nasiyaga olinganda firma tanlang.")
        self.firm_info_label.setWordWrap(True)
        self.firm_info_label.setStyleSheet("color: #6a6a8a; font-size: 12px; background: transparent;")
        firm_layout.addWidget(self.firm_info_label)
        
        form_layout.addRow(firm_group)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        save_btn = QPushButton("💾 Saqlash")
        save_btn.setObjectName("successButton")
        save_btn.setMinimumHeight(45)
        save_btn.clicked.connect(self.save_product)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Bekor qilish")
        cancel_btn.setObjectName("dangerButton")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.payment_type_combo.currentTextChanged.connect(self.on_firm_visibility_changed)
        self.firm_combo.currentIndexChanged.connect(self.on_firm_selected)
    
    def _load_folders(self):
        """Chapdagi 'Kategoriyalar' panelidagi papkalarni combo'ga yuklash"""
        self.folder_input.clear()
        self.folder_input.addItem("— Papka tanlanmagan —", None)
        try:
            category_controller = CategoryController()
            categories = category_controller.get_all()
            category_controller.close()
            for cat in categories:
                self.folder_input.addItem(f"{cat.get('icon') or '📁'} {cat['name']}", cat['id'])
        except Exception as e:
            print(f"❌ Papkalarni yuklashda xatolik: {e}")

    def load_data(self):
        if self.product_data:
            self.name_input.setText(self.product_data.get('name', ''))
            set_category_combo_value(self.category_input, self.product_data.get('category', ''))
            
            self.cost_price_input.setValue(self.product_data.get('cost_price', 0))
            self.sell_price_input.setValue(self.product_data.get('sell_price', 0))
            
            self.dollar_cost_input.setValue(self.product_data.get('dollar_cost', 0))
            self.dollar_sell_input.setValue(self.product_data.get('dollar_price', 0))
            
            rate = self.product_data.get('exchange_rate', 12600)
            self.exchange_rate_input.setValue(rate)
            
            self.quantity_input.setValue(self.product_data.get('quantity', 0))
            self.unit_input.setCurrentText(self.product_data.get('unit', 'dona'))
            self.min_quantity_input.setValue(self.product_data.get('min_quantity', 5))
            self.note_input.setText(self.product_data.get('note', ''))

            # Tahrirlashda - mahsulot hozir turgan papkani belgilab qo'yish
            current_folder_id = self.product_data.get('category_id')
            if current_folder_id:
                idx = self.folder_input.findData(current_folder_id)
                if idx >= 0:
                    self.folder_input.setCurrentIndex(idx)

        self.update_purchase_preview()
    
    def load_firms(self):
        try:
            firms = self.firm_controller.get_all()
            
            self.firm_combo.clear()
            self.firm_combo.addItem("— Firma tanlang —", None)
            
            for firm in firms:
                debt_text = f" (qarz: {firm['total_debt']:,.0f} so'm)" if firm['total_debt'] > 0 else ""
                self.firm_combo.addItem(f"{firm['name']}{debt_text}", firm['id'])
            
        except Exception as e:
            print(f"❌ Firmalarni yuklashda xatolik: {e}")
    
    def on_firm_selected(self, index):
        if self.firm_combo.currentData():
            self.firm_info_label.setText("✅ Firma tanlandi. Qarz avtomatik firma hisobiga yoziladi.")
            self.firm_info_label.setStyleSheet("color: #00c853; font-size: 12px; background: transparent;")
        else:
            self.firm_info_label.setText("⚠️ Iltimos, firma tanlang! Firma qarziga avtomatik qo'shiladi.")
            self.firm_info_label.setStyleSheet("color: #f59e0b; font-size: 12px; background: transparent;")
    
    def on_firm_visibility_changed(self, text):
        is_nasiya = "Nasiya" in text
        self.firm_combo.parent().parent().setVisible(is_nasiya)
        
        if is_nasiya:
            self.on_firm_selected(0)
        else:
            self.firm_info_label.setText("💡 Nasiyaga olinganda firma tanlash mumkin.")
            self.firm_info_label.setStyleSheet("color: #6a6a8a; font-size: 12px; background: transparent;")
    
    def show_add_firm_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("➕ Yangi firma qo'shish")
        dialog.setFixedSize(500, 450)
        dialog.setStyleSheet(DARK_STYLE)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Firma nomi")
        name_input.setMinimumHeight(40)
        name_input.setStyleSheet("""
            QLineEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 10px 15px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        form_layout.addRow("Nomi:", name_input)
        
        phone_input = QLineEdit()
        phone_input.setPlaceholderText("+998 99 123 45 67")
        phone_input.setMinimumHeight(40)
        phone_input.setStyleSheet("""
            QLineEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 10px 15px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        form_layout.addRow("Telefon:", phone_input)
        
        address_input = QLineEdit()
        address_input.setPlaceholderText("Manzil")
        address_input.setMinimumHeight(40)
        address_input.setStyleSheet("""
            QLineEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 10px 15px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        form_layout.addRow("Manzil:", address_input)
        
        note_input = QTextEdit()
        note_input.setMaximumHeight(80)
        note_input.setPlaceholderText("Qo'shimcha ma'lumot...")
        note_input.setStyleSheet("""
            QTextEdit {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 10px 15px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid #6c63ff;
            }
        """)
        form_layout.addRow("Izoh:", note_input)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        save_btn = QPushButton("💾 Saqlash")
        save_btn.setObjectName("successButton")
        save_btn.setMinimumHeight(40)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Bekor qilish")
        cancel_btn.setObjectName("dangerButton")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        def save_firm():
            name = name_input.text().strip()
            if not name:
                QMessageBox.warning(dialog, "Xatolik", "Iltimos, firma nomini kiriting!")
                return
            
            firm_data = {
                'name': name,
                'phone': phone_input.text().strip(),
                'address': address_input.text().strip(),
                'note': note_input.toPlainText().strip(),
                'total_debt': 0
            }
            
            result = self.firm_controller.create(firm_data)
            if result:
                QMessageBox.information(dialog, "Muvaffaqiyat", "✅ Firma muvaffaqiyatli qo'shildi!")
                dialog.accept()
                self.load_firms()
            else:
                QMessageBox.warning(dialog, "Xatolik", "Firma qo'shishda xatolik!")
        
        save_btn.clicked.connect(save_firm)
        dialog.exec()

    def on_category_changed(self, index):
        data = self.category_input.itemData(index, Qt.ItemDataRole.UserRole)
        if data == CUSTOM_CATEGORY_TEXT:
            text, ok = QInputDialog.getText(self, "Yangi kategoriya", "Kategoriya nomini kiriting:")
            text = text.strip() if text else ""
            if ok and text:
                set_category_combo_value(self.category_input, text)
            else:
                self.category_input.setCurrentIndex(0)

    def _get_rate(self):
        return self.exchange_rate_input.value()
    
    def on_auto_rate_toggled(self, checked):
        self.exchange_rate_input.setReadOnly(checked)
        self.auto_rate_btn.setEnabled(True)
        if checked:
            self.load_current_rate()
    
    def load_current_rate(self):
        try:
            rate = get_usd_rate()
            if rate > 0:
                self.exchange_rate_input.setValue(rate)
                self.exchange_rate_input.setStyleSheet("""
                    QDoubleSpinBox {
                        background: #1a2a1a;
                        border: 2px solid #00c853;
                        border-radius: 8px;
                        padding: 8px 12px;
                        color: #00c853;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QDoubleSpinBox:focus {
                        border: 2px solid #6c63ff;
                    }
                """)
                print(f"✅ Kurs avtomatik yuklandi: 1$ = {rate:,.2f} so'm")
                QTimer.singleShot(3000, self._reset_rate_style)
            else:
                self.exchange_rate_input.setStyleSheet("""
                    QDoubleSpinBox {
                        background: #2a1a1a;
                        border: 2px solid #ff6b6b;
                        border-radius: 8px;
                        padding: 8px 12px;
                        color: #ff6b6b;
                        font-size: 14px;
                    }
                    QDoubleSpinBox:focus {
                        border: 2px solid #6c63ff;
                    }
                """)
                print("⚠️ Kurs yuklanmadi")
        except Exception as e:
            print(f"❌ Kurs yuklashda xatolik: {e}")
    
    def _reset_rate_style(self):
        self.exchange_rate_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #14142a;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #6c63ff;
            }
        """)
    
    def on_rate_changed(self):
        if self._updating:
            return
        self._updating = True
        rate = self._get_rate()
        if rate > 0:
            dollar_cost = self.dollar_cost_input.value()
            dollar_sell = self.dollar_sell_input.value()
            if dollar_cost > 0:
                self.cost_price_input.setValue(round(dollar_cost * rate, 0))
            if dollar_sell > 0:
                self.sell_price_input.setValue(round(dollar_sell * rate, 0))
        self._updating = False
    
    def on_cost_price_changed(self):
        if self._updating:
            return
        self._updating = True
        rate = self._get_rate()
        if rate > 0:
            som = self.cost_price_input.value()
            if som > 0:
                self.dollar_cost_input.setValue(round(som / rate, 2))
        self._updating = False
    
    # ===== TUZATILGAN: on_dollar_cost_changed (round qilmasdan) =====
    def on_dollar_cost_changed(self):
        if self._updating:
            return
        self._updating = True
        rate = self._get_rate()
        if rate > 0:
            dollar = self.dollar_cost_input.value()
            if dollar > 0:
                self.cost_price_input.setValue(dollar * rate)
        self._updating = False
    
    def on_sell_price_changed(self):
        if self._updating:
            return
        self._updating = True
        rate = self._get_rate()
        if rate > 0:
            som = self.sell_price_input.value()
            if som > 0:
                self.dollar_sell_input.setValue(round(som / rate, 2))
        self._updating = False
    
    # ===== TUZATILGAN: on_dollar_sell_changed (round qilmasdan) =====
    def on_dollar_sell_changed(self):
        if self._updating:
            return
        self._updating = True
        rate = self._get_rate()
        if rate > 0:
            dollar = self.dollar_sell_input.value()
            if dollar > 0:
                self.sell_price_input.setValue(dollar * rate)
        self._updating = False

    def on_purchase_payment_changed(self, text):
        is_credit = "Nasiya" in text
        for child in self.findChildren(QWidget):
            if isinstance(child, QDateEdit) and child != self.purchase_date_input:
                child.setVisible(is_credit)
            if isinstance(child, QLabel) and "📅 To'lov muddati:" in child.text():
                child.setVisible(is_credit)

    def update_purchase_preview(self):
        old_quantity = self.product_data.get('quantity', 0) if self.product_data else 0
        added_quantity = max(0, self.quantity_input.value() - old_quantity)
        if added_quantity > 0:
            total_cost = added_quantity * self.cost_price_input.value()
            rate = self._get_rate()
            self.purchase_hint_label.setText(
                f"➕ Qo'shilayotgan: {added_quantity:g} dona/birlik  •  "
                f"Xarid summasi: {total_cost:,.0f} so'm  •  "
                f"Kurs: 1$ = {rate:,.0f} so'm"
            )
        else:
            self.purchase_hint_label.setText(
                "Miqdorni ko'paytirsangiz, qo'shilgan qism yetkazib beruvchidan\n"
                "shu to'lov turi bilan olingan deb qayd etiladi."
            )

    def _log_purchase(self, product_id, product_name, added_quantity, firm_id=None):
        try:
            if isinstance(product_id, dict):
                product_id = product_id.get('id', 0)
            elif isinstance(product_id, str):
                product_id = int(product_id)
            
            if not product_id:
                print(f"❌ product_id topilmadi")
                return
            
            payment_type = "Nasiya" if "Nasiya" in self.payment_type_combo.currentText() else "Naxt"
            unit_cost = self.cost_price_input.value()
            dollar_cost = self.dollar_cost_input.value()
            exchange_rate = self.exchange_rate_input.value()
            
            purchase_date = self.purchase_date_input.date().toString("yyyy-MM-dd")
            due_date = None
            if payment_type == "Nasiya":
                due_date = self.due_date_input.date().toString("yyyy-MM-dd")
                print(f"📝 Nasiya qarz: {product_name} - {added_quantity} dona, Kurs: {exchange_rate} (qarz olingan kun)")

            purchase_data = {
                'product_id': int(product_id),
                'product_name': str(product_name),
                'quantity': float(added_quantity),
                'unit_cost': float(unit_cost),
                'total_cost': float(unit_cost * added_quantity),
                'payment_type': str(payment_type),
                'purchase_date': str(purchase_date),
                'due_date': str(due_date) if due_date else None,
                'dollar_cost': float(dollar_cost),
                'exchange_rate': float(exchange_rate),
                'firm_id': firm_id if payment_type == "Nasiya" else None,
            }

            result = PurchaseRepository().create_purchase(purchase_data)
            
            if result:
                print(f"✅ Xarid yozildi: {product_name} - {added_quantity} dona, {payment_type}, Kurs: {exchange_rate}, ID: {result}")
            else:
                print(f"❌ Xarid yozilmadi!")
                
        except Exception as e:
            print(f"❌ Xarid yozuvini saqlashda xatolik: {e}")
            import traceback
            traceback.print_exc()

    def save_product(self):
        try:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Xatolik", "Iltimos, mahsulot nomini kiriting!")
                return
            
            final_image_path = None
            
            old_quantity = self.product_data.get('quantity', 0) if self.product_data else 0
            new_quantity = self.quantity_input.value()
            added_quantity = new_quantity - old_quantity
            
            category_value = self.category_input.currentData(Qt.ItemDataRole.UserRole) or ""
            if category_value == CUSTOM_CATEGORY_TEXT:
                category_value = ""

            product_data = {
                'name': name,
                'category': category_value,
                'cost_price': self.cost_price_input.value(),
                'sell_price': self.sell_price_input.value(),
                'dollar_cost': self.dollar_cost_input.value(),
                'dollar_price': self.dollar_sell_input.value(),
                'exchange_rate': self.exchange_rate_input.value(),
                'quantity': new_quantity,
                'unit': self.unit_input.currentText(),
                'min_quantity': self.min_quantity_input.value(),
                'note': self.note_input.toPlainText().strip(),
                'image_path': final_image_path
            }
            
            product_id = None
            
            if self.product_data and self.product_data.get('id'):
                product_data['id'] = self.product_data['id']
                result = self.product_controller.update_product(product_data)
                if result:
                    if isinstance(result, dict):
                        product_id = result.get('id')
                    else:
                        product_id = self.product_data.get('id')
                    QMessageBox.information(self, "Muvaffaqiyat", "✅ Mahsulot muvaffaqiyatli yangilandi!")
                else:
                    QMessageBox.warning(self, "Xatolik", "Mahsulotni yangilashda xatolik!")
                    return
            else:
                result = self.product_controller.create_product(product_data)
                if result:
                    if isinstance(result, dict):
                        product_id = result.get('id')
                    else:
                        product_id = result
                    QMessageBox.information(self, "Muvaffaqiyat", "✅ Mahsulot muvaffaqiyatli qo'shildi!")
                else:
                    QMessageBox.warning(self, "Xatolik", "Mahsulot qo'shishda xatolik!")
                    return
            
            # ===== PAPKAGA (KATEGORIYAGA) BIRIKTIRISH =====
            if product_id:
                try:
                    selected_folder_id = self.folder_input.currentData()
                    category_controller = CategoryController()
                    category_controller.assign_products([product_id], selected_folder_id)
                    category_controller.close()
                except Exception as e:
                    print(f"❌ Papkaga biriktirishda xatolik: {e}")

            selected_firm_id = None
            if added_quantity > 0 and "Nasiya" in self.payment_type_combo.currentText():
                selected_firm_id = self.firm_combo.currentData()
                if selected_firm_id:
                    debt_amount = added_quantity * self.cost_price_input.value()
                    self.firm_controller.add_debt(selected_firm_id, debt_amount)
                    print(f"✅ Firma qarziga qo'shildi: {debt_amount:,.0f} so'm")
                    QMessageBox.information(
                        self, 
                        "Ma'lumot", 
                        f"✅ Firma qarziga {debt_amount:,.0f} so'm qo'shildi!"
                    )
                else:
                    QMessageBox.warning(
                        self, 
                        "Ogohlantirish", 
                        "⚠️ Nasiyaga olingan, lekin firma tanlanmagan! Qarz firmaga yozilmadi."
                    )
            
            if added_quantity > 0 and product_id:
                self._log_purchase(product_id, name, added_quantity, firm_id=selected_firm_id)

            # ===== MUHIM: hamma narsa muvaffaqiyatli tugagach dialogni yopish =====
            # Shu qator bo'lmagani uchun "Saqlash" bosilganda oyna yopilmay,
            # shuning uchun ProductManagement tarafida load_categories() ham
            # ishga tushmay, papka yonidagi son (0) yangilanmay qolar edi.
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Saqlashda xatolik: {str(e)}")
            print(f"❌ Save error: {e}")
            import traceback
            traceback.print_exc()