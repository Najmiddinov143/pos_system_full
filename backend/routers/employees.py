# backend/routers/employees.py

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from .auth import get_current_user, get_pool
from database import rows_to_dicts, row_to_dict

router = APIRouter()


class EmployeeCreate(BaseModel):
    full_name: str
    phone: str = ""
    position: str
    salary: float = 0
    hire_date: str = ""
    is_active: int = 1


@router.get("/")
async def get_all_employees(request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM employees WHERE is_active = 1 ORDER BY full_name"
        )
    return rows_to_dicts(rows)


@router.get("/{employee_id}")
async def get_employee_by_id(employee_id: int, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM employees WHERE id = $1", employee_id)
    if not row:
        raise HTTPException(status_code=404, detail="Employee not found")
    return row_to_dict(row)


@router.post("/")
async def create_employee(emp: EmployeeCreate, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO employees (full_name, phone, position, salary, hire_date)
               VALUES ($1, $2, $3, $4, $5) RETURNING *""",
            emp.full_name, emp.phone, emp.position, emp.salary, emp.hire_date,
        )
    return row_to_dict(row)


@router.put("/{employee_id}")
async def update_employee(employee_id: int, emp: EmployeeCreate, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """UPDATE employees SET full_name=$1, phone=$2, position=$3,
               salary=$4, hire_date=$5, is_active=$6 WHERE id=$7 RETURNING *""",
            emp.full_name, emp.phone, emp.position, emp.salary,
            emp.hire_date, emp.is_active, employee_id,
        )
    if not row:
        raise HTTPException(status_code=404, detail="Employee not found")
    return row_to_dict(row)


@router.delete("/{employee_id}")
async def delete_employee(employee_id: int, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE employees SET is_active = 0 WHERE id = $1", employee_id
        )
    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted"}


# Attendance
@router.get("/{employee_id}/attendance/{date}")
async def get_attendance(employee_id: int, date: str, request: Request):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM attendance WHERE employee_id = $1 AND date = $2",
            employee_id, date,
        )
    return row_to_dict(row) if row else None


@router.post("/{employee_id}/check-in")
async def check_in(employee_id: int, request: Request, date: str = "", time: str = ""):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO attendance (employee_id, check_in, date) VALUES ($1, $2, $3)",
            employee_id, time, date,
        )
    return {"message": "Checked in"}


@router.post("/{employee_id}/check-out")
async def check_out(employee_id: int, request: Request, date: str = "", time: str = ""):
    get_current_user(request)
    pool = get_pool(request)
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE attendance SET check_out = $1 WHERE employee_id = $2 AND date = $3",
            time, employee_id, date,
        )
    return {"message": "Checked out"}
