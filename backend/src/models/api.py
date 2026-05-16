
import enum

from pydantic import BaseModel, Field


class Qualifier(enum.Enum):
    IN = "in"
    NOT_IN = "not_in"
    EQUALS = "eq"
    NOT_EQUALS = "not_eq"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"


class FilterReq(BaseModel):
    field: str
    qualifier: Qualifier = Qualifier.EQUALS
    value: str | int | list[str | int]


class Filter(FilterReq):
    # since pydantic does not allow for nullable defaults, this wrapper is used
    qualifier: Qualifier | None = Field(default=None, description="If null, defaults to 'eq'.")

class QueryReq(BaseModel):
    term: str | None = None
    filters: list[Filter] = []
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1)
    sort_by: str | None = None
    sort_desc: bool = False


class Query(QueryReq):
    # since pydantic does not allow for nullable defaults, this wrapper is used
    filters: list[Filter] | None = Field(default=None, description="If null, defaults to empty list.")
    offset: int | None = Field(default=None, ge=0, description="If null, defaults to 0.")
    limit: int | None = Field(default=None, ge=1, description="If null, defaults to 10.")
    sort_desc: bool | None = Field(default=None, description="If null, defaults to False.")

