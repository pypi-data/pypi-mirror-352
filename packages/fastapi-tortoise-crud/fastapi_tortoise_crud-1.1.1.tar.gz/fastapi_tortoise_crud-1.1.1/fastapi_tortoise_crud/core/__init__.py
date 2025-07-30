"""
核心模块

包含FastAPI Tortoise CRUD的核心功能
"""

from .base import FastCRUD
from .models import BaseModel
from .schemas import BaseResponse, PaginatedResponse
from .types import CrudConfig

__all__ = [
    "FastCRUD",
    "BaseModel", 
    "BaseResponse",
    "PaginatedResponse",
    "CrudConfig"
]
