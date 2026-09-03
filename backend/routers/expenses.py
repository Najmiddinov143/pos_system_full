# backend/routers/expenses.py

from datetime import date, datetime
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from .auth import get_current_user, get_pool
from database import rows_to_dicts

def _parse_date(val):
    """Convert string to date object for asyncpg compatibility."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    if isinstance(val, str) and val.strip():
        try:
            return datetime.strptime(val.strip(), "%Y-%m-%d").date()
        except ValueError:
            return None
    return None

router = APIRouter()


class ExpenseCreate(BaseModel):
    name: str
    amount: float
    category: str
    description: str = ""
    payment_type: str = "Naxt"
    user_id: Optional[int] = None


@router.get("/")
async def get_all_expenses(
    request: Request, start_date: str = None, end_date: str = None
):
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        # Convert date strings to date objects for asyncpg
        start_date = _parse_date(start_date)
        end_date = _parse_date(end_date)
        if start_date and end_date:
            rows = await conn.fetch(
                """SELECT * FROM expenses
                   WHERE DATE(created_at) BETWEEN DATE($1) AND DATE($2)
                   ORDER BY created_at DESC""",
                start_date, end_date,
            )
        else:
            rows = await conn.fetch("SELECT * FROM expenses ORDER BY created_at DESC")
    return rows_to_dicts(rows)


@router.get("/total")
async def get_total_expenses(
    request: Request, start_date: str = None, end_date: str = None
):
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        # Convert date strings to date objects for asyncpg
        start_date = _parse_date(start_date)
        end_date = _parse_date(end_date)
        if start_date and end_date:
            result = await conn.fetchval(
                """SELECT COALESCE(SUM(amount), 0) FROM expenses
                   WHERE DATE(created_at) BETWEEN DATE($1) AND DATE($2)""",
                start_date, end_date,
            )
        else:
            result = await conn.fetchval("SELECT COALESCE(SUM(amount), 0) FROM expenses")
    return {"total": float(result or 0)}


@router.get("/by-category")
async def get_expenses_by_category(
    request: Request, start_date: str = None, end_date: str = None
):
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        # Convert date strings to date objects for asyncpg
        start_date = _parse_date(start_date)
        end_date = _parse_date(end_date)
        if start_date and end_date:
            rows = await conn.fetch(
                """SELECT category, SUM(amount) as total, COUNT(*) as count
                   FROM expenses WHERE DATE(created_at) BETWEEN DATE($1) AND DATE($2)
                   GROUP BY category ORDER BY total DESC""",
                start_date, end_date,
            )
        else:
            rows = await conn.fetch(
                """SELECT category, SUM(amount) as total, COUNT(*) as count
                   FROM expenses GROUP BY category ORDER BY total DESC"""
            )
    return rows_to_dicts(rows)


@router.post("/")
async def create_expense(expense: ExpenseCreate, request: Request):
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO expenses (name, amount, category, description, payment_type, user_id)
               VALUES ($1, $2, $3, $4, $5, $6)""",
            expense.name, expense.amount, expense.category,
            expense.description, expense.payment_type, expense.user_id,
        )
    return {"message": "Expense created"}


@router.delete("/{expense_id}")
async def delete_expense(expense_id: int, request: Request):
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM expenses WHERE id = $1", expense_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted"}
