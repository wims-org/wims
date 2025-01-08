from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel


class Item(BaseModel):
    container_tag_id: UUID
    short_name: str
    description: Optional[str] = None
    amount: int
    category_tags: List[str]
    images: List[str] = []
    storage_location: Optional[str] = None
    storage_location_tag_id: Optional[str] = None
    current_location: Optional[str] = None
    borrowed_by: Optional[str] = None
    cost_per_item: Optional[float] = None
    manufacturer: Optional[str] = None
    model_number: Optional[str] = None
    upc: Optional[str] = None
    asin: Optional[str] = None
    serial_number: Optional[str] = None
    vendor: Optional[str] = None
    shop_url: Optional[str] = None
    container_size: Optional[str] = None
    consumable: bool
    documentation: Optional[str] = None
