import asyncio
import json
import mimetypes
import time
from pathlib import Path

import openai
import pydantic
from fastapi import APIRouter, HTTPException
from sqlmodel import select

from dependencies.database import SessionDep
from dependencies.event_handler import Event, EventHandlerDep, SseEvent, SseEventData
from dependencies.llm import LLMDep
from dependencies.settings import SettingsDep
from models.item import File, FilePublic

router = APIRouter(prefix="/identification", tags=["identification"], responses={404: {"description": "Not found"}})


class EmptyResponseException(Exception):
    pass


class IdentificationRequest(pydantic.BaseModel):
    query: str | None = None
    client_id: str
    file_ids: list[int] = []


@router.post("")
async def identification(
    body: IdentificationRequest,
    event_handler: EventHandlerDep,
    llm_dep: LLMDep,
    session: SessionDep,
    settings: SettingsDep,
):
    if not body.query and not body.file_ids:
        raise HTTPException(status_code=400, detail="query or file_ids is required")

    # Load file records and read image bytes from disk
    images: list[tuple[bytes, str]] = []
    file_records: list[FilePublic] = []
    if body.file_ids:
        result = await session.execute(select(File).where(File.id.in_(body.file_ids)))
        db_files = result.scalars().all()
        for f in db_files:
            path = settings.data_path / settings.asset_uri_prefix.lstrip("/") / Path(f.uri).name
            if not path.exists():
                continue
            mime = mimetypes.guess_type(str(path))[0] or "image/jpeg"
            images.append((path.read_bytes(), mime))
            file_records.append(FilePublic.model_validate(f))

    async def start_identification(start_time: float):
        chatgpt_response = None
        try:
            chatgpt_response = llm_dep.identify_object(query=body.query, images=images)
            if (
                not chatgpt_response
                or not chatgpt_response.choices
                or not chatgpt_response.choices[0].message
                or not chatgpt_response.choices[0].message.content
            ):
                raise EmptyResponseException("Empty response from LLM")

        except (openai.APIConnectionError, EmptyResponseException, Exception) as e:
            sse_message = SseEvent(
                data=SseEventData(
                    data={"message": str(e)},
                    reader_id=body.client_id,
                    rfid="",
                    duration=time.time() - start_time,
                ).model_dump(mode="json"),
                event=Event.ERROR,
            )
            await event_handler.append_message_to_queue(body.client_id, sse_message)
            return

        result = json.loads(chatgpt_response.choices[0].message.content)
        if file_records:
            result["files"] = [f.model_dump(mode="json") for f in file_records]

        sse_message = SseEvent(
            data=SseEventData(
                reader_id=body.client_id,
                data={
                    "response": result,
                    "tokens": chatgpt_response.usage.total_tokens,
                    "duration": time.time() - start_time,
                },
            ).model_dump(mode="json"),
            event=Event.IDENTIFICATION,
        )
        await event_handler.append_message_to_queue(body.client_id, sse_message)

    asyncio.create_task(start_identification(time.time()))
    return {"message": "Identification process started"}
