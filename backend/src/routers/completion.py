import asyncio
import base64
import json
import logging
import os
import time
from typing import Annotated

import pydantic
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.datastructures import FormData

from dependencies.backend_service import BackendService, Event, SseMessage

router = APIRouter(prefix="/completion",
                   tags=["completion"], responses={404: {"description": "Not found"}})

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)


def get_bs(request: Request) -> BackendService:
    return request.app.state.backend_service


class IdentificationRequest(pydantic.BaseModel):
    data: pydantic.Json | None = None
    images: list[UploadFile] = None


@router.post("/identification")
async def identification(
    request: Request,
    # identificationRequest: IdentificationRequest
    # data: Annotated[FormData, Form()],
    images: list[UploadFile] | None = File(None),
):
    try:
        data = json.loads(dict(request._form.items()).get("data"))
        query = data.get("query")
        client_id = data.get("client_id", [])
        logger.info(data)
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

    async def start_identification(start_time: float):
        if os.environ.get("LLM_ENVIRONMENT") == "development":
            chatgpt_response = {'response': {'upc': None, 'asin': None, 'tags': ['sensor', 'humidity', 'temperature', 'DHT'], 'vendors': ['Adafruit', 'SparkFun', 'Amazon'], 'cost_new': 10.0, 'shop_url': ['https://www.adafruit.com/product/393', 'https://www.sparkfun.com/products/10167', 'https://www.amazon.com/dp/B07D3FQZ3D'], 'cost_used': 5.0, 'item_type': 'sensor',
                                            'consumable': False, 'short_name': 'DHT22 Sensor', 'description': 'DHT22 (AM2302) is a digital temperature and humidity sensor.', 'manufacturer': 'AOSONG', 'model_number': 'AM2302', 'documentation': ['https://www.adafruit.com/product/393', 'https://learn.adafruit.com/dht/overview'], 'serial_number': None}, 'tokens': 1452, 'duration': 7.048832893371582}
            sse_message = SseMessage(
                data=SseMessage.SseMessageData(
                    reader_id=client_id,
                    data= chatgpt_response,
                ),
                event=Event.COMPLETION,
            ).model_dump(mode="json", exclude_none=True)
            get_bs(request).readers.setdefault(client_id, []).append(sse_message)
            return



        chatgpt_response = get_bs(
            request).llm_completion.identify_object(query, encoded_images)
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
                reader_id=client_id,
                data={
                    "response": json.loads(chatgpt_response.choices[0].message.content),
                    "tokens": chatgpt_response.usage.total_tokens,
                    "duration": time.time() - start_time,
                },
            ).model_dump(mode="json"),
            event=Event.COMPLETION,
        ).model_dump(mode="json")
        get_bs(request).readers.setdefault(client_id, []).append(sse_message)

    asyncio.create_task(start_identification(time.time()))
    return {"message": "Identification process started"}
