from sqlmodel import Field, SQLModel

from models.base import SQLModelBase


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: str | None = Field(default=None, unique=True, index=True)
    

class User(UserBase, SQLModelBase, table=True):
    pass

class UserPublic(UserBase):
    pass

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass
