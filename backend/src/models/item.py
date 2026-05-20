import enum
from datetime import datetime
from typing import Optional

from pydantic import computed_field, model_serializer
from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel

from .base import SQLModelBase
from .category import Category
from .user import User


class FileType(enum.Enum):
    IMAGE = "image"
    MANUAL = "manual"
    DRIVER = "driver"
    FIRMWARE = "firmware"


class FileBase(SQLModel):
    item_id: int | None = Field(default=None, foreign_key="item.id")
    uri: str = Field(unique=True)
    filename: str = Field()
    filetype: FileType = Field()


class File(FileBase, SQLModelBase, table=True):
    item: Optional["Item"] = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="File.item_id", remote_side="Item.id", lazy="selectin")
    )


class FilePublic(FileBase):
    id: int


class FileCreate(FileBase):
    pass


class FileUpdate(FileBase):
    pass


class ItemBase(SQLModel):
    # Mandatory Item Information
    short_name: str
    container_id: int | None = Field(default=None, foreign_key="item.id")

    # UUID of the RFID tag, unique
    code: str | None = Field(
        unique=True, index=True, nullable=True, default=None
    )  # ToDo multiple codes/code formats per item
    amount: int | None = None
    # Item type, e.g. "tool", "consumable", "euro_container", "gridfinity_container"
    category_id: int | None = Field(default=None, foreign_key="category.id")
    consumable: bool = False

    # Item Details
    description: str | None = None
    min_amount: int | None = None  # Minimum amount of items, for alerts
    # custom tags for categorization
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))

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
    last_scanned: datetime | None = None
    owner_id: int | None = Field(default=None, foreign_key="user.id")  # UUID of the user owning the item


class Item(ItemBase, SQLModelBase, table=True):
    category: Optional["Category"] = Relationship(
        sa_relationship_kwargs=dict(remote_side="Category.id", lazy="selectin")
    )

    # We need 'join_depth' for self referencing Relationships
    container: Optional["Item"] = Relationship(
        sa_relationship_kwargs=dict(
            remote_side="Item.id", join_depth=1, lazy="selectin", back_populates="content", post_update=True
        )
    )
    content: list["Item"] = Relationship(
        sa_relationship_kwargs=dict(join_depth=1, lazy="selectin", back_populates="container", post_update=True)
    )

    # We need 'foreign_keys' for relationships with multiple references between the tables
    borrower: Optional["User"] = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="Item.borrower_id", remote_side="User.id", lazy="selectin")
    )
    author: Optional["User"] = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="Item.author_id", remote_side="User.id", lazy="selectin")
    )
    owner: Optional["User"] = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="Item.owner_id", remote_side="User.id", lazy="selectin")
    )

    # files
    files: list["File"] = Relationship(
        sa_relationship_kwargs=dict(lazy="selectin", back_populates="item", remote_side="File.item_id")
    )


class ItemPublic(ItemBase, SQLModelBase):
    category: Category | None = None  # Todo account for new Categories by allowing string?
    container: Item | None = None
    content: list[Item] | None = None
    borrower: User | None = None
    author: User | None = None
    owner: User | None = None  # Todo account for new users by allowing string?
    files: list[FilePublic] | None = None

    @computed_field
    def borrowed(self) -> bool:
        return self.borrower_id is not None

    @computed_field
    def is_container(self) -> bool:
        return bool(self.content)


class ItemCreate(ItemBase):
    tags: set[str] = []
    files: list["FilePublic"] | None = None


class ItemUpdate(ItemBase):
    tags: set[str] = []
    short_name: str | None = None
    code: str | None = None
    files: list["FilePublic"] | None = None

    @model_serializer(mode="wrap")  # noqa: F821
    def _serialize(self, handler):
        d = handler(self)
        d["tags"] = list(self.tags)
        return d


class ItemBacklog(ItemBase):
    """This model is used for weaker validation in eg /backlog route"""

    short_name: str = "New Item"
