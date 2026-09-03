# backend/routers/products.py

from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from typing import Optional

from .auth import get_current_user, get_pool
from database import rows_to_dicts, row_to_dict

router = APIRouter()


class ProductCreate(BaseModel):
    name: str
    category: str = ""
    cost_price: float = 0
    sell_price: float = 0
    quantity: float = 0
    unit: str = "dona"
    min_quantity: float = 5
    note: str = ""
    image_path: str = ""
    barcode: str = ""
    supplier: str = ""
    dollar_cost: float = 0
    dollar_price: float = 0
    exchange_rate: float = 0
    category_id: Optional[int] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    cost_price: Optional[float] = None
    sell_price: Optional[float] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    min_quantity: Optional[float] = None
    note: Optional[str] = None
    image_path: Optional[str] = None
    barcode: Optional[str] = None
    supplier: Optional[str] = None
    dollar_cost: Optional[float] = None
    dollar_price: Optional[float] = None
    exchange_rate: Optional[float] = None
    category_id: Optional[int] = None


@router.get("/")
async def get_all_products(request: Request):
    """Get all active products."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM products WHERE is_active = 1 ORDER BY name"
        )
    return rows_to_dicts(rows)


@router.get("/{product_id}")
async def get_product_by_id(product_id: int, request: Request):
    """Get a product by ID."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM products WHERE id = $1", product_id
        )

    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    return row_to_dict(row)


@router.get("/search/{name}")
async def search_products(name: str, request: Request):
    """Search products by name."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM products WHERE name ILIKE $1 AND is_active = 1 ORDER BY name",
            f"%{name}%"
        )
    return rows_to_dicts(rows)


@router.post("/")
async def create_product(product: ProductCreate, request: Request):
    """Create a new product."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO products (
                name, category, cost_price, sell_price, quantity, unit,
                min_quantity, note, image_path, barcode, supplier,
                dollar_cost, dollar_price, exchange_rate, category_id
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            RETURNING *""",
            product.name, product.category, product.cost_price, product.sell_price,
            product.quantity, product.unit, product.min_quantity, product.note,
            product.image_path, product.barcode, product.supplier,
            product.dollar_cost, product.dollar_price, product.exchange_rate,
            product.category_id,
        )

    return row_to_dict(row)


@router.put("/{product_id}")
async def update_product(product_id: int, product: ProductUpdate, request: Request):
    """Update a product."""
    get_current_user(request)
    pool = get_pool(request)

    # Build dynamic SET clause
    updates = {k: v for k, v in product.model_dump(exclude_unset=True).items()}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    set_parts = []
    values = []
    for i, (key, val) in enumerate(updates.items(), 1):
        set_parts.append(f"{key} = ${i}")
        values.append(val)

    values.append(product_id)
    query = f"UPDATE products SET {', '.join(set_parts)} WHERE id = ${len(values)} RETURNING *"

    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, *values)

    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    return row_to_dict(row)


@router.delete("/{product_id}")
async def delete_product(product_id: int, request: Request):
    """Soft delete a product (set is_active = 0)."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE products SET is_active = 0 WHERE id = $1", product_id
        )

    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted", "id": product_id}


@router.post("/{product_id}/restore")
async def restore_product(product_id: int, request: Request):
    """Restore a soft-deleted product."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE products SET is_active = 1 WHERE id = $1", product_id
        )

    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product restored", "id": product_id}


@router.put("/{product_id}/stock")
async def update_stock(product_id: int, quantity_change: float, request: Request):
    """Update product stock quantity."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        # Get current quantity
        row = await conn.fetchrow(
            "SELECT quantity FROM products WHERE id = $1", product_id
        )
        if not row:
            raise HTTPException(status_code=404, detail="Product not found")

        new_qty = round(float(row["quantity"]) + quantity_change, 3)
        if abs(new_qty) < 0.001:
            new_qty = 0

        await conn.execute(
            "UPDATE products SET quantity = $1 WHERE id = $2", new_qty, product_id
        )

    return {"message": "Stock updated", "product_id": product_id, "new_quantity": new_qty}
