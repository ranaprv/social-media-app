"""Shared pagination schemas."""
from pydantic import BaseModel
from typing import TypeVar, Generic, Optional

T = TypeVar("T")


class PaginationParams(BaseModel):
    offset: int = 0
    limit: int = 20


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    offset: int
    limit: int
