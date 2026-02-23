from __future__ import annotations

from models.base import PydanticModelBase, SQLModelBase


class Category(SQLModelBase, table=True):
    __tablename__: str = "category"
    parent_id: str | None = None
    title: str
    description: str | None


class CategoryCreate(PydanticModelBase):
    parent_id: str | None = None
    title: str
    description: str | None = None


class CategoryUpdate(PydanticModelBase):
    parent_id: str | None = None
    title: str | None = None
    description: str | None = None
