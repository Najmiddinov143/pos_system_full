# backend/routers/auth.py

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import bcrypt

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class LoginResponse(BaseModel):
    id: int
    username: str
    role: str
    api_key: str


# Simple API key store (in production, use JWT or DB-stored keys)
# For now, we generate a simple token from user_id + timestamp
import hashlib
import time


def generate_api_key(user_id: int, username: str) -> str:
    """Generate a simple API key from user info."""
    raw = f"pos_system_{user_id}_{username}_{int(time.time())}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


# Store active sessions: api_key -> {user_id, username, role}
_active_sessions: dict = {}


def get_current_user(request: Request) -> dict:
    """Extract current user from API key header."""
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key not in _active_sessions:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return _active_sessions[api_key]


def get_pool(request: Request):
    return request.app.state.pool


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, request: Request):
    """Authenticate user and return API key."""
    pool = get_pool(request)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, username, password_hash, role FROM users WHERE username = $1",
            req.username
        )

    if not row:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user = dict(row)

    if not bcrypt.checkpw(req.password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    api_key = generate_api_key(user["id"], user["username"])
    _active_sessions[api_key] = {
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"],
    }

    return LoginResponse(
        id=user["id"],
        username=user["username"],
        role=user["role"],
        api_key=api_key,
    )


@router.post("/logout")
async def logout(request: Request):
    """Remove API key from active sessions."""
    api_key = request.headers.get("X-API-Key")
    if api_key and api_key in _active_sessions:
        del _active_sessions[api_key]
    return {"message": "Logged out"}


@router.get("/me")
async def get_me(request: Request):
    """Get current user info."""
    user = get_current_user(request)
    return user


@router.get("/users")
async def get_all_users(request: Request):
    """Get all users (admin only)."""
    user = get_current_user(request)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    pool = get_pool(request)
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, username, role, created_at FROM users ORDER BY id")
    return [dict(r) for r in rows]


@router.post("/users")
async def create_user(request: Request, username: str, password: str, role: str = "cashier"):
    """Create a new user (admin only)."""
    user = get_current_user(request)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    pool = get_pool(request)
    pwd_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                "INSERT INTO users (username, password_hash, role) VALUES ($1, $2, $3) RETURNING id, username, role",
                username, pwd_hash, role
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Username already exists: {e}")

    return dict(row)


@router.post("/change-password")
async def change_password(req: ChangePasswordRequest, request: Request):
    """Change the current user's password (any authenticated user)."""
    user = get_current_user(request)
    pool = get_pool(request)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, password_hash FROM users WHERE id = $1",
            user["user_id"],
        )

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    stored_hash = row["password_hash"]
    if not bcrypt.checkpw(req.old_password.encode("utf-8"), stored_hash.encode("utf-8")):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    new_hash = bcrypt.hashpw(req.new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET password_hash = $1 WHERE id = $2", new_hash, user["user_id"])

    return {"message": "Password changed successfully"}


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, request: Request):
    """Delete a user (admin only, cannot delete admin)."""
    user = get_current_user(request)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    pool = get_pool(request)
    async with pool.acquire() as conn:
        # Prevent deleting admin
        admin_check = await conn.fetchval(
            "SELECT username FROM users WHERE id = $1", user_id
        )
        if admin_check == "admin":
            raise HTTPException(status_code=400, detail="Cannot delete admin user")

        result = await conn.execute("DELETE FROM users WHERE id = $1", user_id)

    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}
