from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import Column, String, text
from sqlmodel import Field, SQLModel


class SQLModelBase(SQLModel):
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(String(36), primary_key=True, server_default=text("UUID()")),
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": text("current_timestamp(0)")},
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={
            "server_default": text("current_timestamp(0)"),
            "onupdate": text("current_timestamp(0)"),
        },
    )


class PydanticModelBase(BaseModel):
    class Config:
        orm_mode = True