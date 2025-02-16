import asyncio
import base64
import json
import logging
import time
from typing import Annotated

import pydantic
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from dependencies.backend_service import BackendService, Event, SseMessage

router = APIRouter(
    prefix="/completion", tags=["completion"], responses={404: {"description": "Not found"}})

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)


def get_bs(request: Request) -> BackendService:
    return request.app.state.backend_service


# Database Proxy

@router.post("/object-identification")
async def identify_item(request: Request, file: Annotated[bytes, File()]):
    photo = file
    query_params = dict(request.query_params)
    if "reader_id" not in query_params and "client_id" not in query_params:
        raise HTTPException(
            status_code=400, detail="Missing reader_id or client_id")
    sse_client = query_params.get("reader_id", query_params.get("client_id"))

    async def start_identification(start_time: float):
        chatgpt_response = await get_bs(request).llm_completion.identify_object(photo)
        if (
            not chatgpt_response
            or not chatgpt_response.choices
            or not chatgpt_response.choices[0].message
            or not chatgpt_response.choices[0].message.content
        ):
            sse_message = SseMessage(
                data=SseMessage.SseMessageData(
                    reader_id=sse_client, rfid="", duration=time.time.now() - start_time
                ).model_dump(mode="json"),
                event=Event.ERROR,
            ).model_dump(mode="json")
            get_bs(request).readers.setdefault(
                sse_client, []).append(sse_message)
            return
        logger.debug(f"ChatGPT response: {chatgpt_response}")
        sse_message = SseMessage(
            data=SseMessage.SseMessageData(
                reader_id=sse_client, rfid=chatgpt_response, duration=time.time.now() -
                start_time
            ).model_dump(mode="json"),
            event=Event.COMPLETION,
        ).model_dump(mode="json")
        get_bs(request).readers.setdefault(
            sse_client, []).append(sse_message)

    asyncio.create_task(start_identification(time.time()))
    return {"message": "Identification process started"}


class IdentificationRequest(pydantic.BaseModel):
    data: pydantic.Json | None = None
    images: list[UploadFile] = None


@router.post("/identification")
async def identification(
    # identificationRequest: IdentificationRequest):
    request: Request,
    data: pydantic.Json = Form(...),
    images: list[UploadFile] = File(...),
):
    try:
        query = data.get("query", None)
        client_id = data.get("client_id", [])
        encoded_images = []
        for image in images or []:
            encoded_image = base64.b64encode(await image.read()).decode("utf-8")
            encoded_images.append(encoded_image)
        assert (
            query or images) and client_id, "(Query or Image) and client_id is required"
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, detail="Invalid JSON in document") from None
    except AssertionError:
        raise HTTPException(
            status_code=400, detail="Query or Image is required") from None

    async def start_identification( start_time: float):
        chatgpt_response = get_bs(request).llm_completion.identify_object(
            query, encoded_images)
        if (
            not chatgpt_response
            or not chatgpt_response.choices
            or not chatgpt_response.choices[0].message
            or not chatgpt_response.choices[0].message.content
        ):
            sse_message = SseMessage(
                data=SseMessage.SseMessageData(
                    reader_id=client_id, rfid="", duration=time.time() - start_time
                ).model_dump(mode="json"),
                event=Event.ERROR,
            ).model_dump(mode="json")
            get_bs(request).readers.setdefault(
                client_id, []).append(sse_message)
            return
        logger.debug(f"ChatGPT response: {chatgpt_response}")
        sse_message = SseMessage(
            data=SseMessage.SseMessageData(
                reader_id=client_id, rfid=chatgpt_response, duration=time.time() - start_time
            ).model_dump(mode="json"),
            event=Event.COMPLETION,
        ).model_dump(mode="json")
        get_bs(request).readers.setdefault(
            client_id, []).append(sse_message)

    asyncio.create_task(start_identification(time.time()))
    return {"message": "Identification process started"}

