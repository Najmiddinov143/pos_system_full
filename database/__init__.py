# database/__init__.py
from .connection import create_pool, init_db

__all__ = ['create_pool', 'init_db']
