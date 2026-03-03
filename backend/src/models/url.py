from pydantic import Field
from sqlmodel import SQLModel

from .base import SQLModelBase


class UrlBase(SQLModel):
    item_id: int = Field(foreign_key="item.id")  # URL to documentation or more text


class Url(UrlBase, SQLModelBase, table=True):
    pass


class UrlPublic(UrlBase):
    pass


class UrlCreate(UrlBase):
    pass


class UrlUpdate(UrlBase):
    pass
