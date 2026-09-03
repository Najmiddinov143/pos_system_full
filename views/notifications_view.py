# views/notifications_view.py - O'QILGANDA DOT YO'QOLADI

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils.styles import DARK_STYLE
from controllers.notification_controller import NotificationController
from datetime import datetime, timedelta
import re

class NotificationsView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = NotificationController()
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.load_notifications()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_notifications)
        self.timer.start(30000)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ===== HEADER =====
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #1a1a2e, stop: 1 #2a2a4a);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        
        title = QLabel("🔔 Bildirishnomalar")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # O'qilmaganlar soni (faqat shu sahifada)
        self.unread_badge = QLabel("0")
        self.unread_badge.setStyleSheet("""
            QLabel {
                background: #dc3545;
                color: white;
                border-radius: 12px;
                padding: 4px 12px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        header_layout.addWidget(self.unread_badge)
        
        refresh_btn = QPushButton("🔄 Yangilash")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #6c63ff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #5a52d5;
            }
        """)
        refresh_btn.setMinimumHeight(40)
        refresh_btn.clicked.connect(self.load_notifications)
        header_layout.addWidget(refresh_btn)
        
        layout.addWidget(header_widget)
        
        # ===== FILTR =====
        filter_layout = QHBoxLayout()
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Hammasi", "O'qilmagan", "O'qilgan"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                background: #1a1a2e;
                color: white;
                border: 1px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 14px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #1a1a2e;
                color: white;
                selection-background-color: #4a4a8a;
            }
        """)
        self.filter_combo.currentTextChanged.connect(self.load_notifications)
        filter_layout.addWidget(QLabel("📋 Filtr:"))
        filter_layout.addWidget(self.filter_combo)
        
        filter_layout.addStretch()
        
        mark_all_btn = QPushButton("✅ Hammasini o'qilgan deb belgilash")
        mark_all_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        mark_all_btn.setMinimumHeight(35)
        mark_all_btn.clicked.connect(self.mark_all_as_read)
        filter_layout.addWidget(mark_all_btn)
        
        layout.addLayout(filter_layout)
        
        # ===== TABLE =====
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'ID', '📌 Sarlavha', '💬 Xabar', '📂 Turi', '🕐 Vaqt', '🔴 Holat'
        ])
        self.table.setStyleSheet("""
            QTableWidget {
                background: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 10px;
                alternate-background-color: #222244;
                gridline-color: #2a2a4a;
            }
            QHeaderView::section {
                background: #1a1a32;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #2a2a4a;
                color: #a0a0b8;
                font-weight: bold;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px;
                color: #e0e0e0;
                font-size: 13px;
                border-bottom: 1px solid #2a2a4a;
            }
            QTableWidget::item:selected {
                background: #4a4a8a;
                color: white;
            }
        """)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        
        # Ustun kengliklari
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 350)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(5, 100)
        
        self.table.doubleClicked.connect(self.mark_as_read_from_table)
        
        layout.addWidget(self.table)
        
        # ===== BUTTONS =====
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        read_btn = QPushButton("📖 O'qildi deb belgilash")
        read_btn.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #138496;
            }
        """)
        read_btn.setMinimumHeight(40)
        read_btn.clicked.connect(self.mark_as_read_selected)
        button_layout.addWidget(read_btn)
        
        delete_btn = QPushButton("🗑️ O'chirish")
        delete_btn.setStyleSheet("""
            QPushButton {
                background: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #c82333;
            }
        """)
        delete_btn.setMinimumHeight(40)
        delete_btn.clicked.connect(self.delete_selected)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Eslatma
        note = QLabel("💡 🔴 Qizil = Bugun | 🟡 Sariq = 3 kun ichida | ⚪ Oq = Oddiy / O'qilgan")
        note.setStyleSheet("color: #a0a0b8; font-size: 13px; padding: 10px; background: #1a1a2e; border-radius: 8px;")
        note.setWordWrap(True)
        layout.addWidget(note)
    
    def load_notifications(self):
        """Bildirishnomalarni yuklash"""
        try:
            print("🔄 Bildirishnomalar yuklanmoqda...")
            
            filter_text = self.filter_combo.currentText()
            
            if filter_text == "O'qilmagan":
                notifications = self.controller.get_unread_notifications()
            elif filter_text == "O'qilgan":
                notifications = self.controller.get_read_notifications()
            else:
                notifications = self.controller.get_all_notifications()
            
            # O'qilmaganlar soni
            unread_count = self.controller.get_unread_count()
            self.unread_badge.setText(str(unread_count))
            
            if unread_count > 0:
                self.unread_badge.setStyleSheet("""
                    QLabel {
                        background: #dc3545;
                        color: white;
                        border-radius: 12px;
                        padding: 4px 12px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                """)
            else:
                self.unread_badge.setStyleSheet("""
                    QLabel {
                        background: #28a745;
                        color: white;
                        border-radius: 12px;
                        padding: 4px 12px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                """)
            
            self.table.setRowCount(0)
            
            if not notifications:
                self.table.setRowCount(1)
                empty_item = QTableWidgetItem("📭 Bildirishnomalar yo'q")
                empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                empty_item.setForeground(QColor(160, 160, 184))
                self.table.setItem(0, 0, empty_item)
                self.table.setSpan(0, 0, 1, 6)
                # 🔥 Dot yangilash
                self.update_main_window_dot()
                return
            
            self.table.setRowCount(len(notifications))
            
            today = datetime.now().date()
            
            for i, notif in enumerate(notifications):
                # ID
                id_item = QTableWidgetItem(str(notif.get('id', '')))
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, 0, id_item)
                
                # Sarlavha
                self.table.setItem(i, 1, QTableWidgetItem(notif.get('title', '')))
                
                # Xabar
                self.table.setItem(i, 2, QTableWidgetItem(notif.get('message', '')))
                
                # Turi
                type_item = QTableWidgetItem(notif.get('type', ''))
                type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, 3, type_item)
                
                # Vaqt
                time_item = QTableWidgetItem(notif.get('created_at', ''))
                time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, 4, time_item)
                
                # ===== HOLAT =====
                status_item = QTableWidgetItem()
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                message = notif.get('message', '')
                is_read = notif.get('is_read', True)
                
                status_text = "Oddiy"
                bg_color = QColor(30, 30, 50)
                fg_color = QColor(200, 200, 200)
                status_icon = "⚪"
                
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', message)
                
                if date_match:
                    try:
                        notif_date = datetime.strptime(date_match.group(1), "%Y-%m-%d").date()
                        days_diff = (notif_date - today).days
                        
                        if days_diff == 0:
                            status_icon = "🔴"
                            status_text = "Bugun!"
                            bg_color = QColor(80, 0, 0)
                            fg_color = QColor(255, 100, 100)
                        elif 0 < days_diff <= 3:
                            status_icon = "🟡"
                            status_text = f"{days_diff} kun"
                            bg_color = QColor(80, 60, 0)
                            fg_color = QColor(255, 200, 50)
                        elif days_diff < 0:
                            status_icon = "⚫"
                            status_text = "O'tgan"
                            bg_color = QColor(40, 40, 40)
                            fg_color = QColor(150, 150, 150)
                    except:
                        pass
                
                if not is_read and status_text == "Oddiy":
                    status_icon = "🔴"
                    status_text = "Yangi"
                    bg_color = QColor(60, 0, 0)
                    fg_color = QColor(255, 150, 150)
                elif is_read and status_text == "Oddiy":
                    status_icon = "✅"
                    status_text = "O'qilgan"
                    bg_color = QColor(30, 30, 50)
                    fg_color = QColor(100, 200, 100)
                
                status_item.setText(f"{status_icon} {status_text}")
                status_item.setBackground(bg_color)
                status_item.setForeground(fg_color)
                self.table.setItem(i, 5, status_item)
                
                for col in range(5):
                    item = self.table.item(i, col)
                    if item:
                        if status_text == "Bugun!":
                            item.setBackground(QColor(80, 0, 0))
                            item.setForeground(QColor(255, 100, 100))
                        elif "kun" in status_text and status_text not in ["O'qilgan", "Oddiy"]:
                            item.setBackground(QColor(80, 60, 0))
                            item.setForeground(QColor(255, 200, 50))
                        elif not is_read and status_text == "Yangi":
                            item.setBackground(QColor(60, 0, 0))
                            item.setForeground(QColor(255, 150, 150))
                        elif status_text == "O'qilgan":
                            item.setBackground(QColor(30, 30, 50))
                            item.setForeground(QColor(150, 200, 150))
                        else:
                            item.setBackground(QColor(30, 30, 50))
                            item.setForeground(QColor(200, 200, 200))
            
            print(f"✅ {len(notifications)} ta bildirishnoma yuklandi")
            
            # 🔥 Dot yangilash
            self.update_main_window_dot()
            
        except Exception as e:
            print(f"❌ Xatolik: {e}")
            import traceback
            traceback.print_exc()
    
    def mark_as_read_from_table(self, index):
        try:
            row = index.row()
            if row < 0:
                return
            
            id_item = self.table.item(row, 0)
            if not id_item:
                return
            
            notif_id = int(id_item.text())
            self._mark_single_as_read(notif_id)
            
        except Exception as e:
            print(f"❌ Xatolik: {e}")
    
    def mark_as_read_selected(self):
        try:
            selected = self.table.currentRow()
            if selected < 0:
                QMessageBox.warning(self, "Ogohlantirish", "Iltimos, bildirishnomani tanlang!")
                return
            
            id_item = self.table.item(selected, 0)
            if not id_item:
                return
            
            notif_id = int(id_item.text())
            self._mark_single_as_read(notif_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Xatolik: {str(e)}")
    
    def _mark_single_as_read(self, notif_id):
        try:
            result = self.controller.mark_as_read(notif_id)
            if result:
                print(f"✅ Bildirishnoma #{notif_id} o'qilgan deb belgilandi")
                # 🔥 QAYTA YUKLASH
                self.load_notifications()
                # 🔥 DOT YANGILASH
                self.update_main_window_dot()
            else:
                QMessageBox.warning(self, "Xatolik", "O'qilgan deb belgilashda xatolik!")
                
        except Exception as e:
            print(f"❌ Xatolik: {e}")
    
    def update_main_window_dot(self):
        """Asosiy oynadagi nuqtani yangilash"""
        try:
            main_window = self.window()
            if hasattr(main_window, 'update_notification_dot'):
                main_window.update_notification_dot()
        except Exception as e:
            print(f"❌ Dot yangilashda xatolik: {e}")
    
    def mark_all_as_read(self):
        try:
            reply = QMessageBox.question(
                self, "Tasdiqlash",
                "Barcha bildirishnomalarni o'qilgan deb belgilamoqchimisiz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.controller.mark_all_as_read()
                self.load_notifications()
                self.update_main_window_dot()
                QMessageBox.information(self, "Muvaffaqiyat", "✅ Barcha bildirishnomalar o'qilgan deb belgilandi!")
                
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Xatolik: {str(e)}")
    
    def delete_selected(self):
        try:
            selected = self.table.currentRow()
            if selected < 0:
                QMessageBox.warning(self, "Ogohlantirish", "Iltimos, bildirishnomani tanlang!")
                return
            
            id_item = self.table.item(selected, 0)
            if not id_item:
                return
            
            notif_id = int(id_item.text())
            
            reply = QMessageBox.question(
                self, "Tasdiqlash",
                f"Bildirishnoma #{notif_id} ni o'chirmoqchimisiz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                result = self.controller.delete_notification(notif_id)
                if result:
                    self.load_notifications()
                    self.update_main_window_dot()
                    QMessageBox.information(self, "Muvaffaqiyat", "✅ Bildirishnoma o'chirildi!")
                else:
                    QMessageBox.warning(self, "Xatolik", "O'chirishda xatolik!")
                
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Xatolik: {str(e)}")