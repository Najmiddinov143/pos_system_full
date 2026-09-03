# controllers/product_controller.py

from models.repositories import ProductRepository

class ProductController:
    def __init__(self):
        self.repo = ProductRepository()
    
    def get_all(self, search=""):
        """Barcha mahsulotlarni olish"""
        if search:
            return self.repo.get_product_by_name(search)
        return self.repo.get_all()
    
    def get_all_products(self, search=""):
        return self.get_all(search)
    
    # ===== get_product_by_id metodi =====
    def get_product_by_id(self, product_id):
        """ID bo'yicha mahsulot olish"""
        return self.repo.get_by_id(product_id)
    
    def create_product(self, product_data):
        """Yangi mahsulot qo'shish"""
        if hasattr(product_data, '__dict__'):
            product_data = product_data.__dict__
        
        result = self.repo.create(product_data)
        
        if result:
            print(f"✅ Mahsulot qo'shildi: {result.get('name')} (ID: {result.get('id')})")
            return result
        return None
    
    def update_product(self, product_data):
        if hasattr(product_data, '__dict__'):
            product_data = product_data.__dict__
        return self.repo.update(product_data)
    
    def delete_product(self, product_id):
        return self.repo.delete(product_id)
    
    def update_stock(self, product_id, quantity_change):
        return self.repo.update_stock(product_id, quantity_change)