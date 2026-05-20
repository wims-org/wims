from fastapi import APIRouter, HTTPException
from sqlmodel import select

from dependencies.database import SessionDep
from dependencies.event_handler import EventHandlerDep
from models.api import ElementUpdate, Event, SseEvent, WebhookEvent
from models.reader import Reader, ReaderCreate, ReaderPublic
from modules.webhook_handler import WebhookData, WebhookHandler

router = APIRouter(prefix="/readers", tags=["readers"], responses={404: {"description": "Not found"}})


@router.get("", response_model=list[ReaderPublic])
async def get_readers(session: SessionDep, offset: int = 0, limit: int = 100):
    return (await session.execute(select(Reader).offset(offset).limit(limit))).scalars().all()


@router.get("/{reader_id}", response_model=ReaderPublic)
async def read_reader(session: SessionDep, reader_id: str):
    reader = await session.execute(select(Reader).where(Reader.reader_id == reader_id))
    reader = reader.scalar_one_or_none()
    if not reader:
        raise HTTPException(status_code=400, detail="Reader id not found")
    return reader


@router.post("", response_model=ReaderPublic)
async def create_reader(session: SessionDep, reader: ReaderCreate, event_handler: EventHandlerDep):
    db_reader = Reader.model_validate(reader)
    reader = await session.execute(select(Reader).where(Reader.reader_id == db_reader.reader_id))
    reader = reader.scalar_one_or_none()
    if reader:
        return reader
    session.add(db_reader)
    await session.commit()
    await session.refresh(db_reader)
    await event_handler.append_message_to_all_queues(
        SseEvent(
            data={"element": ElementUpdate.READERS},
            event=Event.ELEMENT_UPDATE,
        )
    )
    WebhookHandler.send_webhook(WebhookData(event_type=WebhookEvent.READER_CREATE, data=db_reader))
    return db_reader


@router.delete("/{id}", response_model=dict)
async def delete_reader(session: SessionDep, id: int, event_handler: EventHandlerDep):
    reader = await session.get(Reader, id)
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    await session.delete(reader)
    await session.commit()
    await event_handler.append_message_to_all_queues(
        SseEvent(
            data={"element": ElementUpdate.READERS},
            event=Event.ELEMENT_UPDATE,
        )
    )
    WebhookHandler.send_webhook(WebhookData(event_type=WebhookEvent.READER_DELETE, data=reader))
    return {"ok": True}
