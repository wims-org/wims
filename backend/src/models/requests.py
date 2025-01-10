from pydantic import BaseModel


class ItemRequest(BaseModel):
    container_tag_id: str
    short_name: str
    description: str | None = None
    amount: int
    category_tags: list[str]
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
    vendor: str | None = None
    shop_url: str | None = None
    container_size: str | None = None
    consumable: bool
    documentation: str | None = None
