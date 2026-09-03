# backend/routers/settings.py

from fastapi import APIRouter, HTTPException, Request
import bcrypt
from pydantic import BaseModel
from typing import Optional

from .auth import get_current_user, get_pool
from database import rows_to_dicts, row_to_dict

router = APIRouter()


class ShopSettingsUpdate(BaseModel):
    shop_name: str = ""
    address: str = ""
    phone: str = ""
    logo_path: str = ""
    receipt_footer: str = ""


class SettingUpdate(BaseModel):
    value: str


# ============================================================
# SHOP SETTINGS
# ============================================================

@router.get("/shop")
async def get_shop_settings(request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM shop_settings LIMIT 1")
    return row_to_dict(row) if row else {}


@router.put("/shop")
async def update_shop_settings(settings: ShopSettingsUpdate, request: Request):
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT id FROM shop_settings LIMIT 1")
        if existing:
            await conn.execute(
                """UPDATE shop_settings
                   SET shop_name=$1, address=$2, phone=$3, logo_path=$4, receipt_footer=$5
                   WHERE id=$6""",
                settings.shop_name, settings.address, settings.phone,
                settings.logo_path, settings.receipt_footer, existing["id"],
            )
        else:
            await conn.execute(
                """INSERT INTO shop_settings (shop_name, address, phone, logo_path, receipt_footer)
                   VALUES ($1, $2, $3, $4, $5)""",
                settings.shop_name, settings.address, settings.phone,
                settings.logo_path, settings.receipt_footer,
            )
    return {"message": "Shop settings updated"}


# ============================================================
# KEY-VALUE SETTINGS
# ============================================================

@router.get("/{key}")
async def get_setting(key: str, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT value FROM settings WHERE key = $1", key)
    return {"key": key, "value": row["value"] if row else None}


@router.put("/{key}")
async def set_setting(key: str, setting: SettingUpdate, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO settings (key, value) VALUES ($1, $2) ON CONFLICT (key) DO UPDATE SET value = $2",
            key, setting.value,
        )
    return {"message": f"Setting '{key}' updated"}


class AdminPasswordChange(BaseModel):
    old_password: str
    new_password: str


@router.put("/admin-password")
async def change_admin_password(req: AdminPasswordChange, request: Request):
    """Change admin password."""
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, password_hash FROM users WHERE username = 'admin'"
        )
        if not row:
            raise HTTPException(status_code=404, detail="Admin user not found")

        if not bcrypt.checkpw(req.old_password.encode("utf-8"), row["password_hash"].encode("utf-8")):
            raise HTTPException(status_code=400, detail="Old password is incorrect")

        new_hash = bcrypt.hashpw(req.new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        await conn.execute(
            "UPDATE users SET password_hash = $1 WHERE username = 'admin'",
            new_hash
        )

    return {"message": "Admin password changed successfully"}
