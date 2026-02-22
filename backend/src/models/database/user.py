from collections.abc import Callable
from datetime import datetime
from typing import ClassVar

from sqlalchemy import JSON
from sqlmodel import Column, Field

from models.base import PydanticModelBase, SQLModelBase


class User(SQLModelBase, table=True):
    __tablename__: ClassVar[str | Callable[..., str]] = "users"
    username: str
    tag_uuids: list[str] = Field(
        default_factory=list, sa_column=Column(JSON)
    )  # List of RFID tag UUIDs associated with the user
    email: str | None = Field(default_factory= None, unique=True, index=True)
    date_created: datetime = Field(default_factory=datetime.now)


class UserCreate(PydanticModelBase):
    username: str
    email: str | None = None

class UserUpdate(PydanticModelBase):
    username: str | None = None
    email: str | None = None
    tag_uuids: list[str] | None = None
