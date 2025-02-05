from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ItemRequest(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    tag_uuid: Annotated[str, Field(alias="tag_uuid")]
    short_name: str
    description: str | None = None
    amount: int | None = None
    tags: list[str] = []
    images: list[str] = []
    storage_location: str | None = None
    storage_location_tag_id: str | None = None
    current_location: str | None = None
    borrowed_by: str | None = None
    cost_per_item: float | None = None
    manufacturer: str | None = None
    model_number: str | None = None
    upc: str | None = None
    asin: str | None = None
    serial_number: str | None = None
    vendor: list[str] = []
    shop_url: list[str] = []
    container_size: str | None = None
    consumable: bool | None = None
    documentation: list[str] = []
