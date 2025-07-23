import asyncio
import json
import os
import time

import pydantic
from fastapi import APIRouter, HTTPException, Request, UploadFile
from loguru import logger

from dependencies.backend_service import BackendService, Event, SseMessage

router = APIRouter(prefix="/completion",
                   tags=["completion"], responses={404: {"description": "Not found"}})


def get_bs(request: Request) -> BackendService:
    return request.app.state.backend_service


class IdentificationRequest(pydantic.BaseModel):
    data: pydantic.Json | None = None
    images: list[UploadFile] = None


@router.post("/identification")
async def identification(
    request: Request,
):
    try:
        # Parse JSON data from the request body
        body = await request.json()
        use_camera = body.get("use_camera", "False").lower() == "true"
        query = body.get("query")
        client_id = body.get("client_id")
        imageUrls = body.get("imageUrls", [])  # Base64-encoded image URLs
        # Validate input
        assert (use_camera or query or imageUrls) and client_id, "(use_camera or Query or Image) and client_id is required"
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, detail="Invalid JSON in request body") from None
    except AssertionError:
        raise HTTPException(
            status_code=400, detail="Query or Image is required") from None

    async def start_identification(start_time: float, imageUrls: list[str]):
        if os.environ.get("LLM_ENVIRONMENT") == "development":
            # Mock response for development
            chatgpt_response = {
                "response": {
                    "upc": None,
                    "asin": None,
                    "tags": ["sensor", "humidity", "temperature", "DHT"],
                    "vendors": ["Adafruit", "SparkFun", "Amazon"],
                    "cost_new": 10.0,
                    "shop_url": [
                        "https://www.adafruit.com/product/393",
                        "https://www.sparkfun.com/products/10167",
                        "https://www.amazon.com/dp/B07D3FQZ3D",
                    ],
                    "cost_used": 5.0,
                    "item_type": "sensor",
                    "consumable": False,
                    "short_name": "DHT22 Sensor",
                    "description": "DHT22 (AM2302) is a digital temperature and humidity sensor.",
                    "manufacturer": "AOSONG",
                    "model_number": "AM2302",
                    "documentation": [
                        "https://www.adafruit.com/product/393",
                        "https://learn.adafruit.com/dht/overview",
                    ],
                    "serial_number": None,
                },
                "tokens": 1452,
                "duration": 7.048832893371582,
            }
            sse_message = SseMessage(
                data=SseMessage.SseMessageData(
                    reader_id=client_id,
                    data=chatgpt_response,
                ),
                event=Event.COMPLETION,
            ).model_dump(mode="json", exclude_none=True)
            get_bs(request).readers.setdefault(
                client_id, []).append(sse_message)
            return

        # Call ChatGPT to identify the object
        chatgpt_response = get_bs(
            request).llm_completion.identify_object(query, imageUrls)
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

        sse_message = SseMessage(
            data=SseMessage.SseMessageData(
                reader_id=client_id,
                data={
                    "response": {
                        **json.loads(chatgpt_response.choices[0].message.content),
                        "images": imageUrls,  # Add imageUrls to data.response.images
                    },
                    "tokens": chatgpt_response.usage.total_tokens,
                    "duration": time.time() - start_time,
                },
            ).model_dump(mode="json"),
            event=Event.COMPLETION,
        ).model_dump(mode="json")
        get_bs(request).readers.setdefault(client_id, []).append(sse_message)

    if use_camera:
        # If use_camera is True, start the identification process with camera input
        imageUrls = get_bs(request).camera.get_camera_image_urls()
        if not imageUrls:
            raise HTTPException(
                status_code=400, detail="No images captured from camera")
    asyncio.create_task(start_identification(time.time(), imageUrls))
    return {"message": "Identification process started"}
