from sqlmodel import Field, SQLModel

from .base import SQLModelBase


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: str | None = Field(default=None, unique=True, index=True, nullable=True)
    code: str | None = Field(default=None, nullable=True)


class User(UserBase, SQLModelBase, table=True):
    pass


class UserPublic(UserBase, SQLModelBase):
    id: int = Field(..., nullable=False)


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass
