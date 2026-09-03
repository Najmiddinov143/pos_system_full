# models/firm.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Firm:
    id: Optional[int] = None
    name: str = ""
    phone: str = ""
    address: str = ""
    total_debt: float = 0.0
    note: str = ""
    created_at: datetime = None