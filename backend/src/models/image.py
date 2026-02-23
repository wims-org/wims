from pydantic import Field
from sqlmodel import SQLModel

from models.base import SQLModelBase


class ImageBase(SQLModel):
    item_id: int = Field(foreign_key="item.id")


class Image(ImageBase, SQLModelBase):
    pass


class ImagePublic(ImageBase):
    pass


class ImageCreate(ImageBase):
    pass


class ImageUpdate(ImageBase):
    pass
