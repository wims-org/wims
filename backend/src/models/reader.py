from sqlmodel import Field, SQLModel

from .base import SQLModelBase


class ReaderBase(SQLModel):
    reader_id: str = Field(unique=True, index=True)
    reader_name: str = Field(default=None, nullable=True)


class Reader(ReaderBase, SQLModelBase, table=True):
    pass


class ReaderPublic(ReaderBase, SQLModelBase):
    id: int = Field(..., nullable=False)


class ReaderCreate(ReaderBase):
    pass


class ReaderUpdate(ReaderBase):
    pass
