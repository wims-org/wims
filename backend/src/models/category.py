# ruff: noqa: F821, UP037
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from .base import SQLModelBase


class CategoryBase(SQLModel):
    parent_id: int | None = Field(default=None, foreign_key="category.id")
    title: str
    description: str | None


class Category(CategoryBase, SQLModelBase, table=True):
    # We need 'join_depth' for self referencing Relationships
    parent: Optional["Category"] = Relationship(
        sa_relationship_kwargs=dict(
            remote_side="Category.id", join_depth=1, lazy="selectin", back_populates="children", post_update=True
        )
    )
    children: list["Category"] = Relationship(
        sa_relationship_kwargs=dict(join_depth=1, lazy="selectin", back_populates="parent", post_update=True)
    )


class CategoryPublic(CategoryBase):
    id: int = Field(..., nullable=False)
    parent: Category | None = None
    children: list[Category] | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass
