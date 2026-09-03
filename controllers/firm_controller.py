# controllers/firm_controller.py
from models.repositories import FirmRepository

class FirmController:
    def __init__(self):
        self.repo = FirmRepository()
    
    def get_all(self):
        """Barcha firmalarni olish"""
        return self.repo.get_all()
    
    def get_by_id(self, firm_id):
        """ID bo'yicha firma olish"""
        return self.repo.get_by_id(firm_id)
    
    def get_by_name(self, name):
        """Nom bo'yicha firma qidirish"""
        return self.repo.get_by_name(name)
    
    def create(self, firm_data):
        """Yangi firma qo'shish"""
        return self.repo.create(firm_data)
    
    def update(self, firm_data):
        """Firmani yangilash"""
        return self.repo.update(firm_data)
    
    def delete(self, firm_id):
        """Firmani o'chirish"""
        return self.repo.delete(firm_id)
    
    def add_debt(self, firm_id, amount):
        """Firma qarziga qo'shish"""
        return self.repo.add_debt(firm_id, amount)
    
    def reduce_debt(self, firm_id, amount):
        """Firma qarzidan ayirish"""
        return self.repo.reduce_debt(firm_id, amount)
    
    def get_total_debt(self):
        """Barcha firmalarning jami qarzi"""
        return self.repo.get_total_debt()