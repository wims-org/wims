from datetime import datetime
from typing import Optional

from pydantic import computed_field, model_serializer
from sqlalchemy import JSON, Column
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlmodel import Field, Relationship, SQLModel

from .base import SQLModelBase
from .image import ImagePublic
from .url import UrlPublic
from .user import UserPublic


class ItemBase(SQLModel):
    # Mandatory Item Information
    short_name: str
    container_id: int | None = Field(default=None, foreign_key="item.id")
    is_container: bool = False

    # UUID of the RFID tag, unique
    tag_uuid: str | None = Field(unique=True, index=True)
    amount: int | None = None
    # Item type, e.g. "tool", "consumable", "euro_container", "gridfinity_container"
    category_id: int | None = Field(default=None, foreign_key="category.id")
    consumable: bool = False

    # Item Details
    description: str | None = None
    min_amount: int | None = None  # Minimum amount of items, for alerts
    # custom tags for categorization
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    # Bindata image document id, <16MB, collection "images"
    price_new: int | None = None  # per item in cents when new
    price_used: int | None = None  # per item in cents, for e.g. selling
    acquisition_date: datetime | None = None
    manufacturer: str | None = None
    model_number: str | None = None
    manufacturing_date: datetime | None = None
    serial_number: str | None = None

    # User Information
    author_id: int | None = Field(default=None, foreign_key="user.id")
    borrower_id: int | None = Field(default=None, foreign_key="user.id")  # ToDo make table
    borrowed_at: datetime | None = None
    borrowed_until: datetime | None = None
    owner_id: int | None = Field(default=None, foreign_key="user.id")  # UUID of the user owning the item


class Item(AsyncAttrs, ItemBase, SQLModelBase, table=True):
    container: Optional["Item"] = Relationship(sa_relationship_kwargs=dict(remote_side="Item.id"))


class ItemPublic(ItemBase):
    @computed_field
    def borrowed(self) -> bool:
        return self.borrower_id is not None


class ItemPublicWithRefs(ItemBase, SQLModelBase):
    images: list[ImagePublic] = []
    author: UserPublic | None = None
    borrower: UserPublic | None = None
    owner: UserPublic | None = None
    urls: list[UrlPublic] = []
    container: ItemPublic | None = None


class ItemCreate(ItemBase):
    tags: set[str] = []


class ItemUpdate(ItemBase):
    tags: set[str] = []

    @model_serializer(mode="wrap")  # noqa: F821
    def _serialize(self, handler):
        d = handler(self)
        d["tags"] = list(self.tags)
        return d


class ItemBacklog(ItemBase):
    """This model is used for weaker validation in eg /backlog route"""

    short_name: str = "New Item"
