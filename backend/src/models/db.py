from __future__ import annotations

from datetime import datetime
from typing import Any

from bson import ObjectId
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Size(SQLModel):
    # Size Information in mm
    length: float
    width: float
    height: float


class Change(SQLModel, table=True):
    # Size Information in mm
    ref: str = Field(default_factory=lambda: str(ObjectId()), primary_key=True)
    user: str
    timestamp: int  # Unix timestamp
    diff_from_prev_version: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class Relation(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(ObjectId()), primary_key=True)
    related_tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))  # list of related tags
    tag: list[str] = Field(default_factory=list, sa_column=Column(JSON))  # category or tag of relation
    description: str | None = None


class Category(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(ObjectId()), primary_key=True)
    parent_id: str | None = None
    title: str
    description: str | None


# Field Alias is used to map the old field name to new field name during database migration after changes
class Item(SQLModel, table=True):
    # UUID of the RFID tag, unique
    tag_uuid: str = Field(primary_key=True)

    # Mandatory Item Information
    short_name: str
    amount: int | None = None
    # Item type, e.g. "tool", "consumable", "euro_container", "gridfinity_container"
    item_type: str | None = None
    consumable: bool = False

    # meta data
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str | None = None
    changes: list[Change] = Field(default_factory=list, sa_column=Column(JSON))
    ai_generated: set[str] = Field(default_factory=set, sa_column=Column(JSON))  # List of AI generated tags

    # Item Details
    description: str | None = None
    min_amount: int | None = None  # Minimum amount of items, for alerts
    # custom tags for categorization
    tags: set[str] = Field(default_factory=set, sa_column=Column(JSON))
    # Bindata image document id, <16MB, collection "images"
    images: list[str] = Field(default_factory=list, sa_column=Column(JSON))  # deprecated
    image_urls: list[str] = Field(
        default_factory=list, sa_column=Column(JSON)
    )  # List of URLs to images, for e.g. external images or after migration
    cost_new: float | None = None  # per item in Euros when new
    acquisition_date: int | None = None  # Unix timestamp
    cost_used: float | None = None  # per item in Euros, for e.g. selling
    manufacturer: str | None = None
    model_number: str | None = None
    manufacturing_date: int | None = None  # Unix timestamp
    upc: str | None = None  # Universal Product Code
    asin: str | None = None  # Amazon Standard Identification Number
    serial_number: str | None = None
    vendors: list[str] = Field(default_factory=list, sa_column=Column(JSON))  # List of vendors
    shop_url: list[str] = Field(default_factory=list, sa_column=Column(JSON))  # List of URLs to shops
    size: Size | None = Field(default_factory=Size, sa_column=Column(JSON))  # outer dimensions of the item in mm
    documentation: list[str] = Field(default_factory=list, sa_column=Column(JSON))  # URL to documentation or more text
    related_items: list[Relation] = Field(default_factory=list, sa_column=Column(JSON))  # Related  of related items

    # Container Information
    # UUID of the parent item containing this item
    container_tag_uuid: str | None = None
    is_container: bool | None = None  # aggregated field
    # temporary uuid of the location, for moving items around
    current_location: str | None = None
    # User Information
    borrowed_by: str | None = None  # UUID of the user borrowing the item
    borrowed_at: int | None = None  # Unix timestamp
    borrowed_until: int | None = None  # Unix timestamp
    owner_id: str | None = None  # UUID of the user owning the item
    # owner: User | None | str = None  # User information of the owner

    # Aggregated Fields, remove
    borrowed: bool = False  # aggregated field
    container_name: str | None = None  # denormalized field for easier querying
    # container: Item | None = None  # denormalized field for easier querying
