# backend/routers/firms.py

from datetime import date, datetime
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from .auth import get_current_user, get_pool
from database import rows_to_dicts, row_to_dict

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


class FirmCreate(BaseModel):
    name: str
    phone: str = ""
    address: str = ""
    total_debt: float = 0
    note: str = ""


class FirmUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    total_debt: Optional[float] = None
    note: Optional[str] = None


class FirmDebtCreate(BaseModel):
    firm_id: int
    amount: float
    description: str = ""
    debt_type: str = "qarz"
    firm_name: str = ""


class FirmDebtPaymentRequest(BaseModel):
    paid_amount: float
    paid_date: str = ""
    cash_amount: float = 0
    card_amount: float = 0


# ============================================================
# FIRMS
# ============================================================

@router.get("/")
async def get_all_firms(request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM firms ORDER BY name")
    return rows_to_dicts(rows)


@router.get("/{firm_id}")
async def get_firm_by_id(firm_id: int, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM firms WHERE id = $1", firm_id)
    if not row:
        raise HTTPException(status_code=404, detail="Firm not found")
    return row_to_dict(row)


@router.get("/search/{name}")
async def search_firms(name: str, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM firms WHERE name ILIKE $1 ORDER BY name", f"%{name}%"
        )
    return rows_to_dicts(rows)


@router.post("/")
async def create_firm(firm: FirmCreate, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO firms (name, phone, address, total_debt, note)
               VALUES ($1, $2, $3, $4, $5) RETURNING *""",
            firm.name, firm.phone, firm.address, firm.total_debt, firm.note,
        )
    return row_to_dict(row)


@router.put("/{firm_id}")
async def update_firm(firm_id: int, firm: FirmUpdate, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    updates = {k: v for k, v in firm.model_dump(exclude_unset=True).items()}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    set_parts, values = [], []
    for i, (k, v) in enumerate(updates.items(), 1):
        set_parts.append(f"{k} = ${i}")
        values.append(v)
    values.append(firm_id)
    query = f"UPDATE firms SET {', '.join(set_parts)} WHERE id = ${len(values)} RETURNING *"
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, *values)
    if not row:
        raise HTTPException(status_code=404, detail="Firm not found")
    return row_to_dict(row)


@router.delete("/{firm_id}")
async def delete_firm(firm_id: int, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM firms WHERE id = $1", firm_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Firm not found")
    return {"message": "Firm deleted"}


@router.get("/total-debt/all")
async def get_total_firm_debt(request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        result = await conn.fetchval("SELECT COALESCE(SUM(total_debt), 0) FROM firms")
    return {"total_debt": float(result or 0)}


# ============================================================
# FIRM DEBTS
# ============================================================

@router.get("/debts/{firm_id}")
async def get_firm_debts(firm_id: int, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM firm_debts WHERE firm_id = $1 ORDER BY created_at DESC", firm_id
        )
    return rows_to_dicts(rows)


@router.get("/debts/all/list")
async def get_all_firm_debts(request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM firm_debts ORDER BY created_at DESC")
    return rows_to_dicts(rows)


@router.post("/debts")
async def create_firm_debt(debt: FirmDebtCreate, request: Request):
    get_current_user(request)
    pool = get_pool(request)

    # Auto-fill firm_name if not provided
    firm_name = debt.firm_name
    if not firm_name:
        async with pool.acquire() as conn:
            row = await conn.fetchval(
                "SELECT name FROM firms WHERE id = $1", debt.firm_id
            )
        firm_name = row or ""

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO firm_debts (firm_id, firm_name, amount, description, debt_type)
               VALUES ($1, $2, $3, $4, $5) RETURNING id""",
            debt.firm_id, firm_name, debt.amount, debt.description, debt.debt_type,
        )
    return {"id": row["id"], "message": "Firm debt created"}


@router.post("/debts/{debt_id}/pay")
async def pay_firm_debt(debt_id: int, payment: FirmDebtPaymentRequest, request: Request):
    """Pay a firm debt with Naxt + Plastik split support."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        debt = await conn.fetchrow("SELECT * FROM firm_debts WHERE id = $1", debt_id)
        if not debt:
            raise HTTPException(status_code=404, detail="Debt not found")

        debt = dict(debt)
        if float(debt["amount"]) <= 0:
            raise HTTPException(status_code=400, detail="Debt already fully paid")

        current_debt = float(debt["amount"])
        paid_amount = float(payment.paid_amount)
        if paid_amount <= 0:
            raise HTTPException(status_code=400, detail="Payment must be > 0")
        if paid_amount > current_debt:
            raise HTTPException(
                status_code=400,
                detail=f"Payment ({paid_amount:,.0f}) > debt ({current_debt:,.0f})"
            )

        cash_amount = float(payment.cash_amount or 0)
        card_amount = float(payment.card_amount or 0)

        if cash_amount > 0 and card_amount > 0:
            if round(cash_amount + card_amount, 2) != round(paid_amount, 2):
                raise HTTPException(
                    status_code=400,
                    detail=f"Cash + Card != Paid amount"
                )
        if cash_amount == 0 and card_amount == 0:
            cash_amount = paid_amount

        if cash_amount > 0 and card_amount > 0:
            payment_type = "Naxt+Plastik"
        elif card_amount > 0:
            payment_type = "Plastik"
        else:
            payment_type = "Naxt"

        remaining = current_debt - paid_amount
        paid_date = payment.paid_date or datetime.now().strftime("%Y-%m-%d")

        if remaining <= 0:
            await conn.execute(
                "UPDATE firm_debts SET amount = 0, is_paid = 1, paid_date = $1 WHERE id = $2",
                paid_date, debt_id
            )
        else:
            await conn.execute(
                "UPDATE firm_debts SET amount = $1, is_paid = 0, paid_date = $2 WHERE id = $3",
                remaining, paid_date, debt_id
            )

        # Record payment
        await conn.execute(
            """INSERT INTO firm_debt_payments
               (debt_id, paid_amount, cash_amount, card_amount, payment_type, paid_date)
               VALUES ($1, $2, $3, $4, $5, $6)""",
            debt_id, paid_amount, cash_amount, card_amount, payment_type, paid_date
        )

        # Reduce firm total_debt
        firm_id = debt.get("firm_id")
        if firm_id:
            await conn.execute(
                "UPDATE firms SET total_debt = GREATEST(0, total_debt - $1) WHERE id = $2",
                paid_amount, firm_id
            )

    return {
        "success": True,
        "remaining_debt": remaining,
        "paid_amount": paid_amount,
        "payment_type": payment_type,
    }


@router.get("/debts/{debt_id}/payments")
async def get_firm_debt_payments(debt_id: int, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM firm_debt_payments WHERE debt_id = $1 ORDER BY created_at DESC",
            debt_id
        )
    return rows_to_dicts(rows)


@router.get("/payments/all/history")
async def get_all_firm_payment_history(
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
                """SELECT * FROM firm_debt_payments
                   WHERE DATE(paid_date) BETWEEN DATE($1) AND DATE($2)
                   ORDER BY paid_date DESC""",
                start_date, end_date
            )
        else:
            rows = await conn.fetch(
                "SELECT * FROM firm_debt_payments ORDER BY paid_date DESC"
            )
    return rows_to_dicts(rows)


@router.get("/payments/summary")
async def get_firm_payment_summary(
    request: Request, firm_id: int = None,
    start_date: str = None, end_date: str = None
):
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        query = """
            SELECT
                COALESCE(SUM(cash_amount), 0) as total_cash,
                COALESCE(SUM(card_amount), 0) as total_card,
                COALESCE(SUM(paid_amount), 0) as total_paid,
                COUNT(*) as payment_count
            FROM firm_debt_payments WHERE 1=1
        """
        params = []
        if firm_id:
            query += " AND debt_id IN (SELECT id FROM firm_debts WHERE firm_id = $1)"
            params.append(firm_id)
        row = await conn.fetchrow(query, *params)

    return dict(row) if row else {"total_cash": 0, "total_card": 0, "total_paid": 0, "payment_count": 0}
