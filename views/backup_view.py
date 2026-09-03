# views/backup_view.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils.styles import DARK_STYLE
from models.repositories import BackupRepository
from datetime import datetime

class BackupView(QWidget):
    def __init__(self):
        super().__init__()
        self.backup_repo = BackupRepository()
        self.setup_ui()
        self.setStyleSheet(DARK_STYLE)
        self.load_backup_history()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        title = QLabel("💾 Zaxiralash (Backup)")
        title.setObjectName("titleLabel")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        backup_btn = QPushButton("🔄 Zaxiralash")
        backup_btn.setObjectName("primaryButton")
        backup_btn.clicked.connect(self.create_backup)
        header_layout.addWidget(backup_btn)
        
        restore_btn = QPushButton("📂 Qayta tiklash")
        restore_btn.setObjectName("warningButton")
        restore_btn.clicked.connect(self.restore_backup)
        header_layout.addWidget(restore_btn)
        
        layout.addLayout(header_layout)
        
        # Info
        info_label = QLabel("💡 Zaxiralash fayllari server-side 'backups' papkasida saqlanadi (PostgreSQL pg_dump).")
        info_label.setStyleSheet("color: #a0a0b8; font-size: 13px; padding: 10px; background: #1a1a2e; border-radius: 8px;")
        layout.addWidget(info_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Sana', 'Fayl nomi', 'Hajmi', 'Kim tomonidan'
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
    
    def create_backup(self):
        try:
            result = self.backup_repo.create_dump()
            if not result or "error" in result:
                detail = result.get("detail", "Noma'lum xatolik") if result else "API xatosi"
                QMessageBox.critical(self, "Xatolik", f"❌ Zaxiralashda xatolik: {detail}")
                return

            file_name = result.get("file_name", "")
            file_size = result.get("file_size", 0)
            QMessageBox.information(
                self,
                "Muvaffaqiyat",
                f"✅ Zaxiralash muvaffaqiyatli!\n📁 {file_name}\n📏 Hajmi: {self._format_size(file_size)}",
            )
            self.load_backup_history()

        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"❌ Zaxiralashda xatolik: {str(e)}")
    
    def restore_backup(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Zaxira SQL faylini tanlang", "backups", "SQL Files (*.sql)"
            )
            if not file_path:
                return

            reply = QMessageBox.question(
                self,
                "Tasdiqlash",
                "⚠️ Ma'lumotlar bazasi qayta tiklanadi (PostgreSQL). Davom etasizmi?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                result = self.backup_repo.restore_dump(file_path)
                if result:
                    QMessageBox.information(self, "Muvaffaqiyat", "✅ Ma'lumotlar bazasi qayta tiklandi!")
                else:
                    QMessageBox.critical(self, "Xatolik", "❌ Qayta tiklashda xatolik!")

        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"❌ Qayta tiklashda xatolik: {str(e)}")
    
    def load_backup_history(self):
        try:
            history = self.backup_repo.get_backup_history(30)

            self.table.setRowCount(len(history))

            for i, b in enumerate(history):
                self.table.setItem(i, 0, QTableWidgetItem(str(b['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(b['backup_date']))
                self.table.setItem(i, 2, QTableWidgetItem(b['file_name']))

                size = b.get('file_size', 0) or 0
                self.table.setItem(i, 3, QTableWidgetItem(self._format_size(size)))

                created_by = b.get('created_by')
                self.table.setItem(i, 4, QTableWidgetItem(str(created_by) if created_by else '-'))

            self.table.resizeColumnsToContents()
        except Exception as e:
            print(f"Error loading backup history: {e}")

    @staticmethod
    def _format_size(size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"