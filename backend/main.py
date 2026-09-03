# backend/main.py - FastAPI Application

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncpg

from database import create_pool, init_db
from routers import auth, products, purchases, sales, expenses, firms, categories
from routers import employees, notifications, settings, reports, incomes, backup

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pos_user:pos_password@localhost:5432/pos_db"
)

# Global connection pool
pool: asyncpg.Pool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    pool = await create_pool()
    await init_db(pool)
    app.state.pool = pool
    print("✅ Database pool created and schema initialized")
    yield
    if pool:
        await pool.close()
        print("✅ Database pool closed")


app = FastAPI(
    title="POS System API",
    description="REST API for POS System - Client-Server Architecture",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(purchases.router, prefix="/api/purchases", tags=["Purchases"])
app.include_router(sales.router, prefix="/api/sales", tags=["Sales"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["Expenses"])
app.include_router(firms.router, prefix="/api/firms", tags=["Firms"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(incomes.router, prefix="/api/incomes", tags=["Incomes"])
app.include_router(backup.router, prefix="/api/backup", tags=["Backup"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "POS System API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
