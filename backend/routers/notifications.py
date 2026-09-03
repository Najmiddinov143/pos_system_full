# backend/routers/notifications.py

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from .auth import get_current_user, get_pool
from database import rows_to_dicts, row_to_dict

router = APIRouter()


class NotificationCreate(BaseModel):
    title: str
    message: str
    type: str = "Eslatma"
    user_id: Optional[int] = None


@router.get("/")
async def get_all_notifications(request: Request, user_id: int = None):
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        if user_id:
            rows = await conn.fetch(
                """SELECT * FROM notifications
                   WHERE user_id = $1 OR user_id IS NULL
                   ORDER BY created_at DESC LIMIT 50""",
                user_id,
            )
        else:
            rows = await conn.fetch(
                "SELECT * FROM notifications ORDER BY created_at DESC LIMIT 50"
            )
    return rows_to_dicts(rows)


@router.get("/unread-count")
async def get_unread_count(request: Request, user_id: int = None):
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        if user_id:
            result = await conn.fetchval(
                """SELECT COUNT(*) FROM notifications
                   WHERE is_read = 0 AND (user_id = $1 OR user_id IS NULL)""",
                user_id,
            )
        else:
            result = await conn.fetchval(
                "SELECT COUNT(*) FROM notifications WHERE is_read = 0"
            )
    return {"count": result or 0}


@router.post("/")
async def create_notification(notif: NotificationCreate, request: Request):
    get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO notifications (title, message, type, user_id, is_read, created_at)
               VALUES ($1, $2, $3, $4, 0, $5) RETURNING id""",
            notif.title, notif.message, notif.type, notif.user_id,
            datetime.now(),
        )
    return {"id": row["id"], "message": "Notification created"}


@router.put("/{notification_id}/read")
async def mark_as_read(notification_id: int, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE notifications SET is_read = 1 WHERE id = $1", notification_id
        )
    return {"message": "Marked as read"}


@router.put("/read-all")
async def mark_all_as_read(request: Request, user_id: int = None):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        if user_id:
            await conn.execute(
                "UPDATE notifications SET is_read = 1 WHERE user_id = $1 OR user_id IS NULL",
                user_id,
            )
        else:
            await conn.execute("UPDATE notifications SET is_read = 1")
    return {"message": "All marked as read"}


@router.delete("/{notification_id}")
async def delete_notification(notification_id: int, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM notifications WHERE id = $1", notification_id)
    return {"message": "Notification deleted"}


@router.delete("/")
async def delete_all_notifications(request: Request, user_id: int = None):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        if user_id:
            await conn.execute(
                "DELETE FROM notifications WHERE user_id = $1 OR user_id IS NULL", user_id
            )
        else:
            await conn.execute("DELETE FROM notifications")
    return {"message": "All notifications deleted"}
