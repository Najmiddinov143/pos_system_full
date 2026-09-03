# controllers/category_controller.py - UPDATED to use API

from models.repositories import CategoryRepository


class CategoryController:
    def __init__(self, db_path=None):
        self.repo = CategoryRepository()

    def _ensure_schema(self):
        pass

    def get_all(self):
        return self.repo.get_all()

    def create(self, name, icon="📁", color=None):
        return self.repo.create(name, icon=icon, color=color)

    def rename(self, category_id, new_name):
        return self.repo.update(category_id, new_name)

    def delete(self, category_id):
        return self.repo.delete(category_id)

    def assign_products(self, product_ids, category_id):
        return self.repo.assign_products(product_ids, category_id)

    def get_products_by_category(self, category_id):
        if category_id is None:
            return []
        return self.repo.get_products_by_category(category_id)

    def get_category_product_count(self, category_id):
        products = self.repo.get_products_by_category(category_id)
        return len(products) if products else 0

    def close(self):
        pass
