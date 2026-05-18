from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import text
from sqlmodel import Field


class SQLModelBase:
    id: int | None = Field(default=None, primary_key=True)

    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"server_default": text("current_timestamp(0)")},
    )

    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={
            "server_default": text("current_timestamp(0)"),
            "onupdate": text("current_timestamp(0)"),
        },
    )


class PydanticModelBase(BaseModel):
    class Config:
        from_attributes = True
