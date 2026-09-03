# controllers/notification_controller.py - TO'LIQ YANGILANGAN

from models.repositories import NotificationRepository
from models.models import Notification
from datetime import datetime
import json
import os

class NotificationController:
    def __init__(self):
        self.notification_repo = NotificationRepository()
        self.sms_sender = None
        
        # Bildirishnomalar uchun JSON fayl (agar DB ishlamasa)
        self.data_file = "data/notifications.json"
        self._ensure_file()
    
    def _ensure_file(self):
        """JSON fayl borligini tekshirish (zaxira)"""
        try:
            os.makedirs("data", exist_ok=True)
            if not os.path.exists(self.data_file):
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _read_json(self):
        """JSON dan o'qish (zaxira)"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _write_json(self, data):
        """JSON ga yozish (zaxira)"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    # ========== SMS XIZMATI ==========
    
    def init_sms(self, email=None, password=None):
        """SMS xizmatini ishga tushirish"""
        try:
            from utils.sms_sender import SmsSender
            if email and password:
                self.sms_sender = SmsSender(email, password)
                return True
            return False
        except Exception as e:
            print(f"❌ SMS xizmatini ishga tushirishda xatolik: {e}")
            return False
    
    def send_sms(self, phone_number, message, from_name="POS Tizimi"):
        """SMS yuborish"""
        try:
            if not self.sms_sender:
                print("❌ SMS xizmati ishga tushmagan!")
                return False
            
            return self.sms_sender.send_sms(phone_number, message, from_name)
        except Exception as e:
            print(f"❌ SMS yuborishda xatolik: {e}")
            return False
    
    def send_test_sms(self, phone_number):
        """Test SMS yuborish"""
        try:
            if not self.sms_sender:
                print("❌ SMS xizmati ishga tushmagan!")
                return False
            
            return self.sms_sender.send_test_sms(phone_number)
        except Exception as e:
            print(f"❌ Test SMS yuborishda xatolik: {e}")
            return False
    
    def get_balance(self):
        """Balansni tekshirish"""
        try:
            if not self.sms_sender:
                print("❌ SMS xizmati ishga tushmagan!")
                return 0
            
            return self.sms_sender.get_balance()
        except Exception as e:
            print(f"❌ Balansni tekshirishda xatolik: {e}")
            return 0
    
    def send_reminder_to_customer(self, customer_data, message_template):
        """Mijozga eslatma SMS yuborish"""
        try:
            if not self.sms_sender:
                print("❌ SMS xizmati ishga tushmagan!")
                return False
            
            phone = customer_data.get('phone_number')
            car_number = customer_data.get('car_number', '')
            next_date = customer_data.get('next_oil_change_date', '')
            
            if not phone:
                print("❌ Telefon raqam yo'q!")
                return False
            
            # Matnni to'ldirish
            message = message_template
            message = message.replace('{car}', car_number)
            message = message.replace('{date}', next_date)
            message = message.replace('{phone}', phone)
            
            return self.sms_sender.send_sms(phone, message)
        except Exception as e:
            print(f"❌ Xatolik: {e}")
            return False
    
    # ========== BILDIRISHNOMALAR (DB) ==========
    
    def create_notification(self, title, message, type_name="Eslatma", user_id=None):
        """Yangi bildirishnoma yaratish (DB ga)"""
        try:
            notification = Notification(
                title=title,
                message=message,
                type=type_name,
                user_id=user_id
            )
            return self.notification_repo.create_notification(notification)
        except Exception as e:
            print(f"❌ DB ga bildirishnoma yaratishda xatolik: {e}")
            # Zaxira: JSON ga yozish
            return self._create_json_notification(title, message, type_name)
    
    def _create_json_notification(self, title, message, type_name="system"):
        """JSON ga bildirishnoma yaratish (zaxira)"""
        try:
            data = self._read_json()
            new_id = max([item.get('id', 0) for item in data]) + 1 if data else 1
            new_notif = {
                'id': new_id,
                'title': title,
                'message': message,
                'type': type_name,
                'is_read': False,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            data.insert(0, new_notif)
            self._write_json(data)
            return new_id
        except Exception as e:
            print(f"❌ JSON ga yozishda xatolik: {e}")
            return None
    
    def get_all_notifications(self, user_id=None):
        """Barcha bildirishnomalarni olish"""
        try:
            # DB dan olish
            result = self.notification_repo.get_all_notifications(user_id)
            if result:
                return result
        except Exception as e:
            print(f"❌ DB dan olishda xatolik: {e}")
        
        # Zaxira: JSON dan olish
        return self._read_json()
    
    def get_unread_notifications(self, user_id=None):
        """O'qilmagan bildirishnomalarni olish"""
        try:
            all_notif = self.get_all_notifications(user_id)
            return [n for n in all_notif if not n.get('is_read', True)]
        except Exception as e:
            print(f"❌ Xatolik: {e}")
            return []
    
    def get_read_notifications(self, user_id=None):
        """O'qilgan bildirishnomalarni olish"""
        try:
            all_notif = self.get_all_notifications(user_id)
            return [n for n in all_notif if n.get('is_read', True)]
        except Exception as e:
            print(f"❌ Xatolik: {e}")
            return []
    
    def mark_as_read(self, notification_id):
        """Bildirishnomani o'qilgan deb belgilash"""
        try:
            # DB dan o'qilgan deb belgilash
            result = self.notification_repo.mark_as_read(notification_id)
            if result:
                return True
        except Exception as e:
            print(f"❌ DB da o'qilgan deb belgilashda xatolik: {e}")
        
        # Zaxira: JSON dan o'qilgan deb belgilash
        try:
            data = self._read_json()
            for item in data:
                if item.get('id') == notification_id:
                    item['is_read'] = True
                    self._write_json(data)
                    return True
        except:
            pass
        
        return False
    
    def mark_all_as_read(self, user_id=None):
        """Hammasini o'qilgan deb belgilash"""
        try:
            # DB dan hammasini o'qilgan deb belgilash
            result = self.notification_repo.mark_all_as_read(user_id)
            if result:
                return True
        except Exception as e:
            print(f"❌ DB da hammasini o'qilgan deb belgilashda xatolik: {e}")
        
        # Zaxira: JSON dan hammasini o'qilgan deb belgilash
        try:
            data = self._read_json()
            for item in data:
                item['is_read'] = True
            self._write_json(data)
            return True
        except:
            pass
        
        return False
    
    def get_unread_count(self, user_id=None):
        """O'qilmagan bildirishnomalar soni"""
        try:
            # DB dan olish
            result = self.notification_repo.get_unread_count(user_id)
            if result is not None:
                return result
        except Exception as e:
            print(f"❌ DB dan unread count olishda xatolik: {e}")
        
        # Zaxira: JSON dan hisoblash
        try:
            data = self._read_json()
            return len([item for item in data if not item.get('is_read', True)])
        except:
            pass
        
        return 0
    
    def delete_notification(self, notification_id):
        """Bildirishnomani o'chirish"""
        try:
            # DB dan o'chirish
            result = self.notification_repo.delete_notification(notification_id)
            if result:
                return True
        except Exception as e:
            print(f"❌ DB dan o'chirishda xatolik: {e}")
        
        # Zaxira: JSON dan o'chirish
        try:
            data = self._read_json()
            data = [item for item in data if item.get('id') != notification_id]
            self._write_json(data)
            return True
        except:
            pass
        
        return False
    
    def delete_all_notifications(self, user_id=None):
        """Barcha bildirishnomalarni o'chirish"""
        try:
            result = self.notification_repo.delete_all_notifications(user_id)
            if result:
                return True
        except Exception as e:
            print(f"❌ DB dan hammasini o'chirishda xatolik: {e}")
        
        # Zaxira: JSON dan hammasini o'chirish
        try:
            self._write_json([])
            return True
        except:
            pass
        
        return False
    
    # ========== QO'SHIMCHA FUNKSIYALAR ==========
    
    def get_notification_by_id(self, notification_id):
        """ID bo'yicha bildirishnomani olish"""
        try:
            all_notif = self.get_all_notifications()
            for n in all_notif:
                if n.get('id') == notification_id:
                    return n
        except:
            pass
        return None
    
    def create_stock_notification(self, product_name, current_qty, min_qty):
        """Zaxirada mahsulot kam qolganda bildirishnoma"""
        title = f"⚠️ Mahsulot kam qolgan"
        message = f"{product_name} - {current_qty} dona qoldi! (Min: {min_qty})"
        return self.create_notification(title, message, "stock")
    
    def create_sale_notification(self, sale_id, customer_name, amount):
        """Sotuv bo'yicha bildirishnoma"""
        title = f"💰 Yangi sotuv"
        message = f"{customer_name} - {amount:,.0f} so'm"
        return self.create_notification(title, message, "sale")
    
    def create_system_notification(self, message):
        """Tizim xatosi haqida bildirishnoma"""
        title = "⚙️ Tizim xabari"
        return self.create_notification(title, message, "system")