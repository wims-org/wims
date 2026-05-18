from typing import Annotated, Any

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, ConfigDict, field_validator
from sqlmodel import select

from dependencies.database import SessionDep
from dependencies.event_handler import EventHandlerDep
from models.api import CodeFormat, Event, SseEvent, SseEventData
from models.item import Item

router = APIRouter(prefix="/scan", responses={404: {"description": "Not found"}})


class ScanRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    reader_id: str
    id: str | int | None = None  # for backwards compatibility, will be mapped to code_value
    code_value: str | None = None
    code_format: CodeFormat | None = CodeFormat.UNKNOWN
    model_config: Annotated[ConfigDict(arbitrary_types_allowed=True), None]

    # temporary solution for backwards compatibility, to be removed in the future
    @field_validator("id", "code_value")
    def check_either_not_none(cls, v: str | None, values: dict, **kwargs: Any) -> str | None:
        if not kwargs.get("validate_assignment"):
            return v
        if v is None and values.get("code_value") is None:
            raise ValueError("either id or code_value must not be None")
        return v


class ScanResponse(BaseModel):
    msg: str
    item_name: str
    item_storage_location: str


@router.post("", response_model=ScanResponse)
async def scan_event(body: ScanRequest, session: SessionDep, event_handler: EventHandlerDep) -> ScanResponse:
    logger.debug(
        f"Scan event from '{body.reader_id}' for '{body.code_value}' ({body.code_format}, {body.model_config})"
    )

    item_res = await session.execute(select(Item).where(Item.code == body.code_value))
    item = item_res.scalars().first()

    await event_handler.append_message_to_all_queues_with_reader(
        reader=body.reader_id,
        message=SseEvent(
            data=SseEventData(
                reader_id=body.reader_id,
                id=item.id if item else None,
                code_value=body.code_value,  # temp, remove id
                code_format=body.code_format,
                data=body.model_config,
            ),
            event=Event.SCAN if item else Event.SCAN_NEW,
        ),
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return ScanResponse(
        msg="Found",
        item_name=item.short_name,
        item_storage_location=item.container.short_name if item.container else "---",
    )
