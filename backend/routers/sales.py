# backend/routers/sales.py

from datetime import date, datetime, timedelta
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List

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


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: float
    sell_price: float
    cost_price: float
    subtotal: float


class SaleCreate(BaseModel):
    total_amount: float
    total_profit: float
    discount: float = 0
    user_id: Optional[int] = None
    car_number: str = ""
    car_model: str = ""
    phone_number: str = ""
    current_km: float = 0
    next_km: float = 0
    oil_change_date: str = ""
    next_oil_change_date: str = ""
    notification_date: str = ""
    is_notified: int = 0
    payment_type: str = "Naxt"
    bonus_amount: float = 0
    discount_amount: float = 0
    cash_amount: float = 0
    card_amount: float = 0
    extra_charge: float = 0
    is_debt: int = 0
    debt_paid: int = 0
    customer_name: str = ""
    customer_phone: str = ""
    items: List[SaleItemCreate] = []


class SaleUpdate(BaseModel):
    payment_type: Optional[str] = None
    car_number: Optional[str] = None
    car_model: Optional[str] = None
    phone_number: Optional[str] = None
    current_km: Optional[float] = None
    next_km: Optional[float] = None
    oil_change_date: Optional[str] = None
    next_oil_change_date: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    discount: Optional[float] = None
    discount_amount: Optional[float] = None
    bonus_amount: Optional[float] = None
    is_debt: Optional[int] = None
    debt_paid: Optional[int] = None
    extra_charge: Optional[float] = None
    total_amount: Optional[float] = None


# ============================================================
# SPECIFIC routes MUST come before parameterized /{sale_id}
# ============================================================

@router.get("/")
async def get_all_sales(request: Request, start_date: str = None, end_date: str = None):
    """Get all sales with items, optionally filtered by date range."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        # Convert date strings to date objects for asyncpg
        start_date = _parse_date(start_date)
        end_date = _parse_date(end_date)
        if start_date and end_date:
            sales_rows = await conn.fetch(
                """SELECT s.*, u.username FROM sales s
                   LEFT JOIN users u ON s.user_id = u.id
                   WHERE DATE(s.created_at) BETWEEN DATE($1) AND DATE($2)
                   ORDER BY s.created_at DESC""",
                start_date, end_date
            )
        else:
            sales_rows = await conn.fetch(
                """SELECT s.*, u.username FROM sales s
                   LEFT JOIN users u ON s.user_id = u.id
                   ORDER BY s.created_at DESC"""
            )

        result = []
        for sale in sales_rows:
            items_rows = await conn.fetch(
                """SELECT si.*, p.name as product_name
                   FROM sale_items si
                   JOIN products p ON si.product_id = p.id
                   WHERE si.sale_id = $1""",
                sale["id"]
            )
            sale_dict = dict(sale)
            sale_dict["items"] = [dict(item) for item in items_rows]
            result.append(sale_dict)

    return result


@router.post("/")
async def create_sale(sale_data: SaleCreate, request: Request):
    """
    Create a new sale. Atomically:
    1. Insert sale record
    2. Insert sale items
    3. Deduct inventory
    4. Log inventory changes
    """
    get_current_user(request)
    pool = get_pool(request)

    if not sale_data.items:
        raise HTTPException(status_code=400, detail="Sale must have at least one item")

    async with pool.acquire() as conn:
        async with conn.transaction():
            sale_row = await conn.fetchrow(
                """INSERT INTO sales (
                    total_amount, total_profit, discount, user_id,
                    car_number, car_model, phone_number, current_km, next_km,
                    oil_change_date, next_oil_change_date, notification_date, is_notified,
                    payment_type, bonus_amount, discount_amount, cash_amount, card_amount,
                    extra_charge, is_debt, debt_paid, customer_name, customer_phone
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13,
                    $14, $15, $16, $17, $18, $19, $20, $21, $22, $23
                ) RETURNING id""",
                sale_data.total_amount, sale_data.total_profit,
                sale_data.discount_amount or sale_data.discount,
                sale_data.user_id,
                sale_data.car_number, sale_data.car_model, sale_data.phone_number,
                sale_data.current_km, sale_data.next_km,
                sale_data.oil_change_date, sale_data.next_oil_change_date,
                sale_data.notification_date or "", sale_data.is_notified,
                sale_data.payment_type, sale_data.bonus_amount,
                sale_data.discount_amount or sale_data.discount,
                sale_data.cash_amount, sale_data.card_amount,
                sale_data.extra_charge, sale_data.is_debt, sale_data.debt_paid,
                sale_data.customer_name, sale_data.customer_phone,
            )
            sale_id = sale_row["id"]

            for item in sale_data.items:
                await conn.execute(
                    """INSERT INTO sale_items
                       (sale_id, product_id, quantity, sell_price, cost_price, subtotal)
                       VALUES ($1, $2, $3, $4, $5, $6)""",
                    sale_id, item.product_id, item.quantity,
                    item.sell_price, item.cost_price, item.subtotal
                )
                qty_row = await conn.fetchrow(
                    "SELECT quantity FROM products WHERE id = $1", item.product_id
                )
                if qty_row:
                    new_qty = round(float(qty_row["quantity"]) - item.quantity, 3)
                    if abs(new_qty) < 0.001:
                        new_qty = 0
                    await conn.execute(
                        "UPDATE products SET quantity = $1 WHERE id = $2",
                        new_qty, item.product_id
                    )
                    await conn.execute(
                        "INSERT INTO inventory_logs (product_id, action, quantity) VALUES ($1, $2, $3)",
                        item.product_id, "sotildi", -item.quantity
                    )

    return {"id": sale_id, "message": "Sale created"}


# --- All SPECIFIC string routes BEFORE /{sale_id} ---

@router.get("/date/{date_str}")
async def get_sales_by_date(date_str: str, request: Request):
    """Get sales for a specific date."""
    get_current_user(request)
    pool = get_pool(request)
    date_str = _parse_date(date_str)
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM sales WHERE DATE(created_at) = DATE($1) ORDER BY created_at DESC",
            date_str
        )
    return rows_to_dicts(rows)


@router.get("/totals/{date_str}")
async def get_sales_totals(date_str: str, request: Request):
    """Get total sales and profit for a date."""
    get_current_user(request)
    pool = get_pool(request)
    date_str = _parse_date(date_str)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """SELECT
                COALESCE(SUM(total_amount), 0) as total,
                COALESCE(COUNT(*), 0) as count,
                COALESCE(SUM(total_profit), 0) as profit
               FROM sales WHERE DATE(created_at) = DATE($1)""",
            date_str
        )
    return dict(row) if row else {"total": 0, "count": 0, "profit": 0}


@router.get("/cash-card-balance/{date_str}")
async def get_cash_card_balance(date_str: str, request: Request):
    """Get cash and card balance for a date."""
    get_current_user(request)
    pool = get_pool(request)
    date_str = _parse_date(date_str)
    async with pool.acquire() as conn:
        sales_row = await conn.fetchrow(
            """SELECT COALESCE(SUM(cash_amount), 0) as cash,
                      COALESCE(SUM(card_amount), 0) as card
               FROM sales WHERE DATE(created_at) = DATE($1)""",
            date_str
        )
        paid_row = await conn.fetchrow(
            """SELECT COALESCE(SUM(cash_amount), 0) as cash,
                      COALESCE(SUM(card_amount), 0) as card
               FROM debt_payments WHERE DATE(paid_date) = DATE($1)""",
            date_str
        )
        firm_row = await conn.fetchrow(
            """SELECT COALESCE(SUM(cash_amount), 0) as cash,
                      COALESCE(SUM(card_amount), 0) as card
               FROM firm_debt_payments WHERE DATE(paid_date) = DATE($1)""",
            date_str
        )
    total_cash = float(sales_row["cash"] or 0)
    total_card = float(sales_row["card"] or 0)
    paid_cash = float(paid_row["cash"] or 0)
    paid_card = float(paid_row["card"] or 0)
    firm_paid_cash = float(firm_row["cash"] or 0)
    firm_paid_card = float(firm_row["card"] or 0)
    return {
        "total_cash": total_cash,
        "total_card": total_card,
        "available_cash": max(0.0, total_cash - paid_cash - firm_paid_cash),
        "available_card": max(0.0, total_card - paid_card - firm_paid_card),
    }


@router.get("/upcoming-notifications")
async def get_upcoming_notifications(request: Request, days: int = 3):
    """Get upcoming oil change notifications."""
    get_current_user(request)
    pool = get_pool(request)
    today = datetime.now().date()
    end_date = today + timedelta(days=days)
    async with pool.acquire() as conn:
        # Convert date strings to date objects for asyncpg
        end_date = _parse_date(end_date)
        sales_rows = await conn.fetch(
            """SELECT s.*, u.username FROM sales s
               LEFT JOIN users u ON s.user_id = u.id
               WHERE DATE(s.next_oil_change_date) BETWEEN $1 AND $2
               AND s.is_notified = 0
               ORDER BY s.next_oil_change_date ASC""",
            today, end_date
        )
        result = []
        for sale in sales_rows:
            items_rows = await conn.fetch(
                """SELECT si.*, p.name as product_name
                   FROM sale_items si JOIN products p ON si.product_id = p.id
                   WHERE si.sale_id = $1""",
                sale["id"]
            )
            sale_dict = dict(sale)
            sale_dict["items"] = [dict(item) for item in items_rows]
            result.append(sale_dict)
    return result


# ============================================================
# NOW the parameterized route
# ============================================================

@router.get("/{sale_id}")
async def get_sale_by_id(sale_id: int, request: Request):
    """Get a sale by ID with items."""
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        sale = await conn.fetchrow(
            """SELECT s.*, u.username FROM sales s
               LEFT JOIN users u ON s.user_id = u.id
               WHERE s.id = $1""",
            sale_id
        )
        if not sale:
            raise HTTPException(status_code=404, detail="Sale not found")
        items_rows = await conn.fetch(
            """SELECT si.*, p.name as product_name
               FROM sale_items si
               JOIN products p ON si.product_id = p.id
               WHERE si.sale_id = $1""",
            sale_id
        )
    sale_dict = dict(sale)
    sale_dict["items"] = [dict(item) for item in items_rows]
    return sale_dict


@router.put("/{sale_id}")
async def update_sale(sale_id: int, update: SaleUpdate, request: Request):
    """Update a sale's metadata (not items)."""
    get_current_user(request)
    pool = get_pool(request)
    updates = {k: v for k, v in update.model_dump(exclude_unset=True).items()}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    set_parts, values = [], []
    for i, (key, val) in enumerate(updates.items(), 1):
        set_parts.append(f"{key} = ${i}")
        values.append(val)
    values.append(sale_id)
    query = f"UPDATE sales SET {', '.join(set_parts)} WHERE id = ${len(values)} RETURNING *"
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, *values)
    if not row:
        raise HTTPException(status_code=404, detail="Sale not found")
    return row_to_dict(row)


@router.put("/{sale_id}/payment-type")
async def update_payment_type(
    sale_id: int,
    request: Request,
    new_payment_type: str = "",
    customer_name: str = "",
    customer_phone: str = "",
):
    """Update sale payment type."""
    get_current_user(request)
    pool = get_pool(request)
    is_debt = 1 if new_payment_type == "Nasiya" else 0
    async with pool.acquire() as conn:
        result = await conn.execute(
            """UPDATE sales SET payment_type = $1, is_debt = $2,
               customer_name = $3, customer_phone = $4 WHERE id = $5""",
            new_payment_type, is_debt, customer_name, customer_phone, sale_id
        )
    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Sale not found")
    return {"message": "Payment type updated"}


@router.put("/{sale_id}/mark-notified")
async def mark_as_notified(sale_id: int, request: Request):
    """Mark sale as notified."""
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        await conn.execute("UPDATE sales SET is_notified = 1 WHERE id = $1", sale_id)
    return {"message": "Marked as notified"}


@router.put("/{sale_id}/reduce-by-payment")
async def reduce_sale_by_payment(
    sale_id: int,
    request: Request,
    total_delta: float = 0,
    cash_delta: float = 0,
    card_delta: float = 0,
):
    """Reduce sale amounts by a debt payment amount."""
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT total_amount, cash_amount, card_amount FROM sales WHERE id = $1",
            sale_id
        )
        if not row:
            raise HTTPException(status_code=404, detail="Sale not found")
        new_total = max(0, float(row["total_amount"] or 0) - total_delta)
        new_cash = max(0, float(row["cash_amount"] or 0) - cash_delta)
        new_card = max(0, float(row["card_amount"] or 0) - card_delta)
        await conn.execute(
            "UPDATE sales SET total_amount = $1, cash_amount = $2, card_amount = $3 WHERE id = $4",
            new_total, new_cash, new_card, sale_id
        )
    return {"message": "Sale reduced by payment"}
