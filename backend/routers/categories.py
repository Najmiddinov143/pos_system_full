# backend/routers/categories.py

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from .auth import get_current_user, get_pool
from database import rows_to_dicts, row_to_dict

router = APIRouter()


class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    icon: str = "📁"
    color: Optional[str] = None


@router.get("/")
async def get_all_categories(request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM categories ORDER BY name")
    return rows_to_dicts(rows)


@router.get("/tree")
async def get_category_tree(request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM categories ORDER BY name")

    cats = [dict(r) for r in rows]
    cats_dict = {c["id"]: {**c, "children": []} for c in cats}
    tree = []
    for c in cats:
        if c["parent_id"] is None:
            tree.append(cats_dict[c["id"]])
        elif c["parent_id"] in cats_dict:
            cats_dict[c["parent_id"]]["children"].append(cats_dict[c["id"]])
    return tree


@router.get("/{category_id}")
async def get_category_by_id(category_id: int, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM categories WHERE id = $1", category_id)
    if not row:
        raise HTTPException(status_code=404, detail="Category not found")
    return row_to_dict(row)


@router.post("/")
async def create_category(cat: CategoryCreate, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                """INSERT INTO categories (name, parent_id, icon, color)
                   VALUES ($1, $2, $3, $4) RETURNING *""",
                cat.name, cat.parent_id, cat.icon, cat.color,
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    return row_to_dict(row)


@router.put("/{category_id}")
async def update_category(category_id: int, cat: CategoryCreate, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """UPDATE categories SET name=$1, parent_id=$2, icon=$3, color=$4
               WHERE id=$5 RETURNING *""",
            cat.name, cat.parent_id, cat.icon, cat.color, category_id,
        )
    if not row:
        raise HTTPException(status_code=404, detail="Category not found")
    return row_to_dict(row)


@router.delete("/{category_id}")
async def delete_category(category_id: int, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE products SET category_id = NULL WHERE category_id = $1", category_id
        )
        result = await conn.execute("DELETE FROM categories WHERE id = $1", category_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted"}


@router.get("/{category_id}/products")
async def get_products_by_category(category_id: int, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM products WHERE category_id = $1 AND is_active = 1 ORDER BY name",
            category_id,
        )
    return rows_to_dicts(rows)


@router.post("/{category_id}/assign-products")
async def assign_products(category_id: int, product_ids: list, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        for pid in product_ids:
            await conn.execute(
                "UPDATE products SET category_id = $1 WHERE id = $2", category_id, pid
            )
    return {"message": f"Assigned {len(product_ids)} products"}
