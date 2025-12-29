from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, computed_field
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class ObjectIdPydanticAnnotation:
    @classmethod
    def validate_object_id(cls, v: Any, handler) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        s = handler(v)
        if ObjectId.is_valid(s):
            return ObjectId(s)
        else:
            raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, _handler) -> core_schema.CoreSchema:
        assert source_type is ObjectId
        return core_schema.no_info_wrap_validator_function(
            cls.validate_object_id,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler) -> JsonSchemaValue:
        return handler(core_schema.str_schema())


class User(BaseModel):
    id: str = Field(alias="_id")  # MongoDB ObjectId
    username: str
    tag_uuids: list[str] = Field(default_factory=list)
    email: str | None = None
    date_created: str | datetime = Field(default_factory=datetime.now)


class Size(BaseModel):
    # Size Information in mm
    length: float
    width: float
    height: float


class Change(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # Size Information in mm
    user: str
    timestamp: int  # Unix timestamp
    diff_from_prev_version: dict[str, Any]


class Relation(BaseModel):
    related_tags: list[str]  # list of related tags
    tag: list[str]  # category or tag of relation
    description: str | None = None


class Category(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    _id: Annotated[ObjectId, ObjectIdPydanticAnnotation] | None = None
    parent_id: Annotated[ObjectId, ObjectIdPydanticAnnotation] | None = None
    title: str
    description: str | None


# Field Alias is used to map the old field name to new field name during database migration after changes
class Item(BaseModel):
    model_config = ConfigDict(populate_by_name=True)  # noqa: F821
    tag_uuid: Annotated[str, Field(alias="tag_uuid")]  # UUID of the item

    # Mandatory Item Information
    short_name: str
    amount: int | None = None
    # Item type, e.g. "tool", "consumable", "euro_container", "gridfinity_container"
    item_type: str | None = None
    consumable: bool = False

    # meta data
    created_at: str | datetime = Field(default_factory=datetime.now)
    created_by: str | None = None
    changes: list[Change] = []
    ai_generated: set[str] = Field(default_factory=set)  # List of AI generated tags

    # Item Details
    description: str | None = None
    min_amount: int | None = None  # Minimum amount of items, for alerts
    # custom tags for categorization
    tags: set[str] = Field(default_factory=set)
    # Bindata image document id, <16MB, collection "images"
    images: list[str] = []
    cost_new: float | None = None  # per item in Euros when new
    acquisition_date: int | None = None  # Unix timestamp
    cost_used: float | None = None  # per item in Euros, for e.g. selling
    manufacturer: str | None = None
    model_number: str | None = None
    manufacturing_date: int | None = None  # Unix timestamp
    upc: str | None = None  # Universal Product Code
    asin: str | None = None  # Amazon Standard Identification Number
    serial_number: str | None = None
    vendors: list[str] = []  # List of vendors
    shop_url: list[str] = []  # List of URLs to shops
    size: Size | None = None  # outer dimensions of the item in mm
    documentation: list[str] = []  # URL to documentation or more text
    related_items: list[Relation] = []  # Related  of related items

    # Container Information
    # UUID of the parent item containing this item
    container_tag_uuid: str | None = None
    container: Item | None = None
    is_container: bool | None = None  # aggregated field
    # temporary uuid of the location, for moving items around
    current_location: str | None = None
    # User Information
    borrowed_by: str | None = None  # UUID of the user borrowing the item
    borrowed_at: int | None = None  # Unix timestamp
    borrowed_until: int | None = None  # Unix timestamp
    owner_id: str | None = None  # UUID of the user owning the item
    # owner: User | None | str = None  # User information of the owner

    @computed_field
    def borrowed(self) -> bool:
        return self.borrowed_by is not None

    @computed_field
    def container_name(self) -> bool:
        if self.container is None:
            return None
        elif isinstance(self.container, Item):
            return self.container.short_name or None
        return self.container.get("short_name", None)
