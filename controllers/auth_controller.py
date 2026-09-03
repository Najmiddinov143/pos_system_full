# from models.repositories import UserRepository
# from models.models import User

# class AuthController:
#     def __init__(self):
#         self.user_repo = UserRepository()
    
#     def login(self, username, password):
#         return self.user_repo.authenticate(username, password)
    
#     def create_user(self, username, password, role):
#         return self.user_repo.create_user(username, password, role)
    
#     def get_all_users(self):
#         return self.user_repo.get_all_users()


# controllers/auth_controller.py

from models.repositories import UserRepository

class AuthController:
    def __init__(self):
        self.user_repo = UserRepository()
    
    def login(self, username, password):
        """Foydalanuvchini tizimga kiritish"""
        try:
            user = self.user_repo.authenticate(username, password)
            if user:
                print(f"✅ User logged in: {username}")
            else:
                print(f"❌ Login failed: {username}")
            return user
        except Exception as e:
            print(f"❌ Login error: {e}")
            return None
    
    def create_user(self, username, password, role):
        """Yangi foydalanuvchi yaratish"""
        try:
            return self.user_repo.create_user(username, password, role)
        except Exception as e:
            print(f"❌ Create user error: {e}")
            return None