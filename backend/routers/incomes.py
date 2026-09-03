# backend/routers/incomes.py

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


class IncomeCreate(BaseModel):
    amount: float
    note: str = ""
    user_id: Optional[int] = None


@router.get("/")
async def get_incomes(request: Request, date: str = None):
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        # Convert date strings to date objects for asyncpg
        date = _parse_date(date)
        if date:
            rows = await conn.fetch(
                """SELECT * FROM cash_incomes
                   WHERE DATE(created_at) = DATE($1)
                   ORDER BY created_at DESC""",
                date,
            )
        else:
            rows = await conn.fetch(
                "SELECT * FROM cash_incomes ORDER BY created_at DESC"
            )
    return rows_to_dicts(rows)


@router.post("/")
async def create_income(income: IncomeCreate, request: Request):
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO cash_incomes (amount, note, user_id) VALUES ($1, $2, $3) RETURNING id",
            income.amount, income.note, income.user_id,
        )
    return {"id": row["id"], "message": "Income created"}


@router.delete("/{income_id}")
async def delete_income(income_id: int, request: Request):
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM cash_incomes WHERE id = $1", income_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Income not found")
    return {"message": "Income deleted"}
