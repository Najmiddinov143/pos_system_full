# utils/sms_sender.py
import requests
import json

class SmsSender:
    def __init__(self, email=None, password=None):
        self.email = email
        self.password = password
        self.token = None
        self.base_url = "https://notify.eskiz.uz/api"
        
        if email and password:
            self.login()
    
    def login(self):
        """Eskiz.uz ga kirish va token olish"""
        try:
            url = f"{self.base_url}/auth/login"
            data = {
                'email': self.email,
                'password': self.password
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    self.token = result.get('data', {}).get('token')
                    print("✅ Token olindi!")
                    return True
                else:
                    print(f"❌ Xatolik: {result}")
                    return False
            else:
                print(f"❌ Xatolik: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Xatolik: {e}")
            return False
    
    def send_sms(self, phone_number, message, from_name="POS Tizimi"):
        """SMS yuborish"""
        try:
            if not self.token:
                if not self.login():
                    return False
            
            phone = phone_number.replace('+', '').replace(' ', '').replace('-', '')
            if not phone.startswith('998'):
                phone = '998' + phone
            
            url = f"{self.base_url}/message/sms/send"
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            data = {
                'mobile_phone': phone,
                'message': message,
                'from': from_name
            }
            
            response = requests.post(url, data=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"✅ SMS yuborildi: {phone}")
                    return True
                else:
                    print(f"❌ Xatolik: {result}")
                    return False
            else:
                print(f"❌ Xatolik: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Xatolik: {e}")
            return False
    
    def send_test_sms(self, phone_number):
        """Test SMS yuborish"""
        return self.send_sms(phone_number, "Bu Eskiz dan test", "Eskiz Test")
    
    def get_balance(self):
        """Balansni tekshirish"""
        try:
            if not self.token:
                self.login()
            
            url = f"{self.base_url}/user/balance"
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('data', {}).get('balance', 0)
            return 0
        except Exception as e:
            print(f"❌ Xatolik: {e}")
            return 0