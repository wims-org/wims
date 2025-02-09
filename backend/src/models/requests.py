from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from models.database import Change, Size


class ItemRequest(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    tag_uuid: Annotated[str, Field(alias="tag_uuid")]
    short_name: str
    description: str | None = None
    amount: int | None = None
    item_type: str | None = None
    consumable: bool | None = None
    created_at: datetime | None = Field(default_factory=datetime.now)
    created_by: str | None = None
    changes: list[Change] = []
    ai_generated: set[str] = Field(default_factory=set)
    min_amount: int | None = None
    tags: set[str] = Field(default_factory=set)
    images: list[str] = []
    cost_new: float | None = None
    acquisition_date: int | None = None
    cost_used: float | None = None
    manufacturer: str | None = None
    model_number: str | None = None
    manufacturing_date: int | None = None
    upc: str | None = None
    asin: str | None = None
    serial_number: str | None = None
    vendors: list[str] = []
    shop_url: list[str] = []
    size: Size | None = None
    documentation: list[str] = []
    container_tag_uuid: str | None = None
    current_location: str | None = None
    borrowed_by: str | None = None
    borrowed_at: int | None = None
    borrowed_until: int | None = None
    owner: str | None = None
