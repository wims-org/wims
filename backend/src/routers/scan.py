from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, ConfigDict
from sqlmodel import select

from dependencies.database import SessionDep
from dependencies.event_handler import Event, EventHandlerDep, SseMessage
from models.item import Item

router = APIRouter(prefix="/scan", responses={404: {"description": "Not found"}})


class ScanRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    reader_id: str
    tag_id: str
    data: dict | str | any = None


class ScanResponse(BaseModel):
    msg: str
    item_name: str
    item_storage_location: str


@router.post("", response_model=ScanResponse)
async def scan_event(body: ScanRequest, session: SessionDep, event_handler: EventHandlerDep) -> ScanResponse:
    logger.debug(f"Scan event from '{body.reader_id}' with tag '{body.tag_id}' and data '{body.data}'")

    await event_handler.append_message_to_all_queues_with_reader(
        reader=body.reader_id,
        message=SseMessage(
            data=SseMessage.SseMessageData(reader_id=body.reader_id, rfid=body.tag_id), event=Event.SCAN
        ),
    )
    item_res = await session.execute(select(Item).where(Item.tag_uuid == body.tag_id))
    item = item_res.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return ScanResponse(
        msg="Found",
        item_name=item.short_name,
        item_storage_location=item.container.short_name if item.container else "---",
    )
