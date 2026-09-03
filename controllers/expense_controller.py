# controllers/expense_controller.py
from models.repositories import ExpenseRepository
from models.models import Expense

class ExpenseController:
    def __init__(self):
        self.expense_repo = ExpenseRepository()
    
    def get_all_expenses(self, start_date=None, end_date=None):
        return self.expense_repo.get_all_expenses(start_date, end_date)
    
    def get_total_expenses(self, start_date=None, end_date=None):
        return self.expense_repo.get_total_expenses(start_date, end_date)
    
    def create_expense(self, expense):
        return self.expense_repo.create_expense(expense)
    
    def delete_expense(self, expense_id):
        return self.expense_repo.delete_expense(expense_id)
    
    def get_expenses_by_category(self, start_date=None, end_date=None):
        return self.expense_repo.get_expenses_by_category(start_date, end_date)