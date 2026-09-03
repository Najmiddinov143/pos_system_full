# backend/routers/purchases.py

from datetime import date, datetime, timedelta
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


class PurchaseCreate(BaseModel):
    product_id: int
    product_name: str = ""
    quantity: float = 0
    unit_cost: float = 0
    total_cost: float = 0
    payment_type: str = "Naxt"
    purchase_date: str = ""
    due_date: Optional[str] = None
    dollar_cost: float = 0
    dollar_price: float = 0
    exchange_rate: float = 0
    firm_id: Optional[int] = None


class PurchaseUpdate(BaseModel):
    payment_type: Optional[str] = None
    due_date: Optional[str] = None
    is_paid: Optional[int] = None
    paid_date: Optional[str] = None


class DebtPaymentRequest(BaseModel):
    paid_amount: float
    paid_date: str = ""
    cash_amount: float = 0
    card_amount: float = 0


@router.get("/")
async def get_all_purchases(
    request: Request,
    product_id: Optional[int] = None
):
    """Get all purchases, optionally filtered by product_id."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        if product_id:
            rows = await conn.fetch(
                "SELECT * FROM stock_purchases WHERE product_id = $1 ORDER BY created_at DESC",
                product_id
            )
        else:
            rows = await conn.fetch(
                "SELECT * FROM stock_purchases ORDER BY created_at DESC"
            )
    return rows_to_dicts(rows)


@router.get("/debts")
async def get_all_debts(request: Request):
    """Get all unpaid nasiya purchases."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT * FROM stock_purchases
               WHERE payment_type = 'Nasiya' AND is_paid = 0
               ORDER BY due_date ASC"""
        )
    return rows_to_dicts(rows)


@router.get("/debts/notifications")
async def get_debt_notifications(request: Request, days: int = 7):
    """Get debt notifications for debts due within N days."""
    get_current_user(request)
    pool = get_pool(request)

    today = datetime.now().date()
    end_date = today + timedelta(days=days)

    async with pool.acquire() as conn:
        # Convert date strings to date objects for asyncpg
        end_date = _parse_date(end_date)
        rows = await conn.fetch(
            """SELECT * FROM stock_purchases
               WHERE payment_type = 'Nasiya' AND is_paid = 0
               AND DATE(due_date) <= $1 AND DATE(due_date) >= $2
               ORDER BY due_date ASC""",
            end_date, today
        )
    return rows_to_dicts(rows)


@router.get("/total-debt")
async def get_total_debt(request: Request):
    """Get total unpaid nasiya debt in UZS."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        result = await conn.fetchval(
            """SELECT COALESCE(SUM(total_cost), 0)
               FROM stock_purchases
               WHERE payment_type = 'Nasiya' AND is_paid = 0"""
        )
    return {"total_debt": float(result or 0)}


@router.get("/total-debt-usd")
async def get_total_debt_usd(request: Request):
    """Get total unpaid nasiya debt in USD."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        result = await conn.fetchval(
            """SELECT COALESCE(SUM(dollar_cost * quantity), 0)
               FROM stock_purchases
               WHERE payment_type = 'Nasiya' AND is_paid = 0"""
        )
    return {"total_debt_usd": float(result or 0)}


@router.get("/{purchase_id}")
async def get_purchase_by_id(purchase_id: int, request: Request):
    """Get a purchase by ID."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM stock_purchases WHERE id = $1", purchase_id
        )

    if not row:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return row_to_dict(row)


@router.post("/")
async def create_purchase(purchase: PurchaseCreate, request: Request):
    """Create a new stock purchase."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO stock_purchases (
                product_id, product_name, quantity, unit_cost, total_cost,
                payment_type, purchase_date, due_date,
                dollar_cost, dollar_price, exchange_rate, firm_id
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING id""",
            purchase.product_id, purchase.product_name, purchase.quantity,
            purchase.unit_cost, purchase.total_cost, purchase.payment_type,
            purchase.purchase_date, purchase.due_date,
            purchase.dollar_cost, purchase.dollar_price, purchase.exchange_rate,
            purchase.firm_id,
        )

    return {"id": row["id"], "message": "Purchase created"}


@router.put("/{purchase_id}")
async def update_purchase(purchase_id: int, update: PurchaseUpdate, request: Request):
    """Update a purchase."""
    get_current_user(request)
    pool = get_pool(request)

    updates = {k: v for k, v in update.model_dump(exclude_unset=True).items()}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    set_parts = []
    values = []
    for i, (key, val) in enumerate(updates.items(), 1):
        set_parts.append(f"{key} = ${i}")
        values.append(val)

    values.append(purchase_id)
    query = f"UPDATE stock_purchases SET {', '.join(set_parts)} WHERE id = ${len(values)} RETURNING *"

    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, *values)

    if not row:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return row_to_dict(row)


@router.delete("/{purchase_id}")
async def delete_purchase(purchase_id: int, request: Request):
    """Delete a purchase and its associated debt payments."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        # Check purchase exists first
        exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM stock_purchases WHERE id = $1)",
            purchase_id,
        )
        if not exists:
            raise HTTPException(status_code=404, detail="Purchase not found")

        # Delete associated debt payments first (FK constraint)
        await conn.execute(
            "DELETE FROM debt_payments WHERE purchase_id = $1", purchase_id
        )

        result = await conn.execute(
            "DELETE FROM stock_purchases WHERE id = $1", purchase_id
        )

    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Purchase not found")
    return {"message": "Purchase deleted"}


# ============================================================
# DEBT PAYMENTS
# ============================================================

@router.post("/{purchase_id}/pay")
async def pay_debt(purchase_id: int, payment: DebtPaymentRequest, request: Request):
    """
    Partially or fully pay a nasiya debt.
    Supports Naxt (cash) + Plastik (card) split payments.
    """
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        # Get purchase
        purchase = await conn.fetchrow(
            "SELECT * FROM stock_purchases WHERE id = $1", purchase_id
        )
        if not purchase:
            raise HTTPException(status_code=404, detail="Purchase not found")

        purchase = dict(purchase)

        if purchase["is_paid"] == 1:
            raise HTTPException(status_code=400, detail="This debt is already fully paid")

        current_debt = float(purchase["total_cost"])
        paid_amount = float(payment.paid_amount)

        if paid_amount <= 0:
            raise HTTPException(status_code=400, detail="Payment amount must be greater than 0")

        if paid_amount > current_debt:
            raise HTTPException(
                status_code=400,
                detail=f"Payment amount ({paid_amount:,.0f}) exceeds debt ({current_debt:,.0f})"
            )

        cash_amount = float(payment.cash_amount or 0)
        card_amount = float(payment.card_amount or 0)

        # Validate cash + card = paid_amount
        if cash_amount > 0 or card_amount > 0:
            if round(cash_amount + card_amount) != round(paid_amount):
                raise HTTPException(
                    status_code=400,
                    detail=f"Cash ({cash_amount:,.0f}) + Card ({card_amount:,.0f}) != Paid ({paid_amount:,.0f})"
                )
        else:
            cash_amount = paid_amount
            card_amount = 0

        # Determine payment type
        if cash_amount > 0 and card_amount > 0:
            payment_type = "Naxt+Plastik"
        elif card_amount > 0:
            payment_type = "Plastik"
        else:
            payment_type = "Naxt"

        remaining_debt = current_debt - paid_amount
        paid_date = payment.paid_date or datetime.now().strftime("%Y-%m-%d")

        # Update purchase
        if remaining_debt <= 0:
            await conn.execute(
                """UPDATE stock_purchases
                   SET is_paid = 1, paid_date = $1, remaining_debt = 0
                   WHERE id = $2""",
                paid_date, purchase_id
            )
        else:
            await conn.execute(
                """UPDATE stock_purchases
                   SET total_cost = $1, remaining_debt = $2, paid_date = $3
                   WHERE id = $4""",
                remaining_debt, remaining_debt, paid_date, purchase_id
            )

        # Record payment
        await conn.execute(
            """INSERT INTO debt_payments
               (purchase_id, paid_amount, cash_amount, card_amount, payment_type, paid_date)
               VALUES ($1, $2, $3, $4, $5, $6)""",
            purchase_id, paid_amount, cash_amount, card_amount, payment_type, paid_date
        )

        # Reduce firm debt if applicable
        firm_id = purchase.get("firm_id")
        if firm_id:
            await conn.execute(
                """UPDATE firms SET total_debt = GREATEST(0, total_debt - $1) WHERE id = $2""",
                paid_amount, firm_id
            )

    status = "fully paid" if remaining_debt <= 0 else f"remaining: {remaining_debt:,.0f}"
    return {
        "success": True,
        "message": f"Debt {status}",
        "remaining_debt": remaining_debt,
        "paid_amount": paid_amount,
        "cash_amount": cash_amount,
        "card_amount": card_amount,
        "payment_type": payment_type,
    }


@router.get("/{purchase_id}/payments")
async def get_payment_history(purchase_id: int, request: Request):
    """Get payment history for a specific purchase debt."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        # Convert date strings to date objects for asyncpg
        rows = await conn.fetch(
            "SELECT * FROM debt_payments WHERE purchase_id = $1 ORDER BY created_at DESC",
            purchase_id
        )
    return rows_to_dicts(rows)


@router.get("/payments/all")
async def get_all_payment_history(
    request: Request,
    start_date: str = None,
    end_date: str = None
):
    """Get all debt payment history."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        # Convert date strings to date objects for asyncpg
        start_date = _parse_date(start_date)
        end_date = _parse_date(end_date)
        if start_date and end_date:
            rows = await conn.fetch(
                """SELECT * FROM debt_payments
                   WHERE DATE(paid_date) BETWEEN DATE($1) AND DATE($2)
                   ORDER BY paid_date DESC""",
                start_date, end_date
            )
        else:
            rows = await conn.fetch(
                "SELECT * FROM debt_payments ORDER BY paid_date DESC"
            )
    return rows_to_dicts(rows)
