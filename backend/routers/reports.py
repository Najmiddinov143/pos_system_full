# backend/routers/reports.py

from fastapi import APIRouter, HTTPException, Request
from datetime import date, datetime, timedelta

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


@router.get("/dashboard")
async def get_dashboard_stats(request: Request):
    get_current_user(request)
    pool = get_pool(request)
    today = datetime.now().date()

    async with pool.acquire() as conn:
        products = await conn.fetchrow(
            """SELECT COUNT(*) as cnt,
                COALESCE(SUM(cost_price * quantity), 0) as total_cost,
                COALESCE(SUM(sell_price * quantity), 0) as total_value
               FROM products WHERE is_active = 1"""
        )

        payment_stats = await conn.fetchrow(
            """SELECT
                COALESCE(SUM(CASE WHEN payment_type = 'Naxt' THEN total_amount ELSE 0 END), 0) as cash,
                COALESCE(SUM(CASE WHEN payment_type = 'Plastik' THEN total_amount ELSE 0 END), 0) as card,
                COALESCE(SUM(CASE WHEN payment_type = 'Nasiya' THEN total_amount ELSE 0 END), 0) as debt,
                COALESCE(SUM(bonus_amount), 0) as bonus_total
               FROM sales WHERE DATE(created_at) = $1""",
            today,
        )

        today_sales = await conn.fetchval(
            "SELECT COALESCE(SUM(total_amount), 0) FROM sales WHERE DATE(created_at) = $1", today
        )
        today_profit = await conn.fetchval(
            """SELECT COALESCE(SUM(total_profit), 0) FROM sales
               WHERE NOT (payment_type = 'Nasiya' AND debt_paid = 0)
               AND DATE(created_at) = $1""",
            today,
        )

        total_profit = await conn.fetchval(
            """SELECT COALESCE(SUM(total_profit), 0) FROM sales
               WHERE NOT (payment_type = 'Nasiya' AND debt_paid = 0)"""
        )

        total_expense = await conn.fetchval("SELECT COALESCE(SUM(amount), 0) FROM expenses")

    p = dict(products) if products else {}
    ps = dict(payment_stats) if payment_stats else {}

    return {
        "products_count": p.get("cnt", 0),
        "total_cost": float(p.get("total_cost", 0)),
        "total_value": float(p.get("total_value", 0)),
        "today_sales": float(today_sales or 0),
        "today_profit": float(today_profit or 0),
        "total_profit": float(total_profit or 0),
        "total_expense": float(total_expense or 0),
        "net_profit": float((total_profit or 0) - (total_expense or 0)),
        "cash_sales": float(ps.get("cash", 0)),
        "card_sales": float(ps.get("card", 0)),
        "debt_sales": float(ps.get("debt", 0)),
        "bonus_total": float(ps.get("bonus_total", 0)),
    }


@router.get("/daily-sales")
async def get_daily_sales(request: Request, days: int = 7):
    get_current_user(request)
    pool = get_pool(request)
    end = datetime.now().date()
    start = end - timedelta(days=days - 1)

    async with pool.acquire() as conn:
        dates, amounts = [], []
        for i in range(days):
            d = start + timedelta(days=i)
            dates.append(d.strftime("%d.%m"))
            result = await conn.fetchval(
                "SELECT COALESCE(SUM(total_amount), 0) FROM sales WHERE DATE(created_at) = $1", d
            )
            amounts.append(float(result or 0))

    return {"dates": dates, "amounts": amounts}


@router.get("/top-products")
async def get_top_products(request: Request, limit: int = 10):
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT p.id, p.name,
                COALESCE(SUM(si.quantity), 0) as total_quantity,
                COALESCE(SUM(si.subtotal), 0) as total_amount,
                COALESCE(SUM(si.subtotal - (si.cost_price * si.quantity)), 0) as total_profit
               FROM sale_items si
               JOIN products p ON si.product_id = p.id
               GROUP BY p.id, p.name
               ORDER BY total_quantity DESC
               LIMIT $1""",
            limit,
        )
    return rows_to_dicts(rows)


@router.get("/sale-items/{sale_id}")
async def get_sale_items(sale_id: int, request: Request):
    """Get sale items by sale_id."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT si.*, p.name as product_name, p.unit
               FROM sale_items si
               JOIN products p ON si.product_id = p.id
               WHERE si.sale_id = $1""",
            sale_id
        )
    return rows_to_dicts(rows)


@router.get("/payment-stats")
async def get_payment_stats(request: Request, start_date: str, end_date: str):
    """Get payment type breakdown for a date range."""
    get_current_user(request)
    pool = get_pool(request)

    # Convert date strings to date objects for asyncpg
    start_date = _parse_date(start_date)
    end_date = _parse_date(end_date)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """SELECT
                COALESCE(SUM(CASE WHEN payment_type = 'Naxt' THEN total_amount ELSE 0 END), 0) as naxt_total,
                COALESCE(SUM(CASE WHEN payment_type = 'Plastik' THEN total_amount ELSE 0 END), 0) as plastik_total,
                COALESCE(SUM(CASE WHEN payment_type = 'Naxt+Plastik' THEN total_amount ELSE 0 END), 0) as mixed_total,
                COALESCE(SUM(CASE WHEN payment_type = 'Naxt+Plastik' THEN cash_amount ELSE 0 END), 0) as mixed_cash,
                COALESCE(SUM(CASE WHEN payment_type = 'Naxt+Plastik' THEN card_amount ELSE 0 END), 0) as mixed_card,
                COALESCE(SUM(CASE WHEN payment_type = 'Naxt' THEN total_profit ELSE 0 END), 0) as naxt_profit,
                COALESCE(SUM(CASE WHEN payment_type = 'Plastik' THEN total_profit ELSE 0 END), 0) as plastik_profit,
                COALESCE(SUM(CASE WHEN payment_type = 'Nasiya' THEN total_profit ELSE 0 END), 0) as debt_profit,
                COALESCE(SUM(total_profit), 0) as total_profit
               FROM sales
               WHERE DATE(created_at) BETWEEN DATE($1) AND DATE($2)""",
            start_date, end_date
        )

        payment_rows = await conn.fetch(
            """SELECT
                payment_type,
                COUNT(*) as count,
                SUM(total_amount) as total,
                SUM(total_profit) as profit
               FROM sales
               WHERE DATE(created_at) BETWEEN DATE($1) AND DATE($2)
               GROUP BY payment_type""",
            start_date, end_date
        )

    if not row:
        return {
            "naxt_total": 0, "plastik_total": 0, "mixed_total": 0,
            "mixed_cash": 0, "mixed_card": 0, "naxt_profit": 0,
            "plastik_profit": 0, "debt_profit": 0, "total_profit": 0,
            "payment_summary": [],
        }

    return {
        "naxt_total": float(row["naxt_total"] or 0),
        "plastik_total": float(row["plastik_total"] or 0),
        "mixed_total": float(row["mixed_total"] or 0),
        "mixed_cash": float(row["mixed_cash"] or 0),
        "mixed_card": float(row["mixed_card"] or 0),
        "naxt_profit": float(row["naxt_profit"] or 0),
        "plastik_profit": float(row["plastik_profit"] or 0),
        "debt_profit": float(row["debt_profit"] or 0),
        "total_profit": float(row["total_profit"] or 0),
        "payment_summary": [dict(r) for r in payment_rows],
    }


@router.get("/sales-for-export")
async def get_sales_for_export(request: Request, start_date: str, end_date: str):
    """Get sales with items for Excel/PDF export."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        # Convert date strings to date objects for asyncpg
        start_date = _parse_date(start_date)
        end_date = _parse_date(end_date)
        sales_rows = await conn.fetch(
            """SELECT s.*, u.username FROM sales s
               LEFT JOIN users u ON s.user_id = u.id
               WHERE DATE(s.created_at) BETWEEN DATE($1) AND DATE($2)
               ORDER BY s.created_at DESC""",
            start_date, end_date
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
