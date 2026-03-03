from __future__ import annotations

from sqlmodel import SQLModel

from .base import SQLModelBase


class CategoryBase(SQLModel):
    parent_id: str | None = None
    title: str
    description: str | None


class Category(CategoryBase, SQLModelBase, table=True):
    pass


class CategoryPublic(CategoryBase):
    pass


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass
