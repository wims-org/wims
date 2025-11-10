import asyncio
import json
import os
import time

import openai
import pydantic
from fastapi import APIRouter, HTTPException, Request, UploadFile
from openai.types.chat.chat_completion import ChatCompletion, ChatCompletionMessage, Choice, CompletionUsage

from dependencies.backend_service import Event, SseMessage
from routers.utils import get_bs

router = APIRouter(prefix="/completion", tags=["completion"], responses={404: {"description": "Not found"}})


class EmptyResponseException(Exception):
    pass


class MockResponseException(Exception):
    pass


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
        query = body.get("query")
        client_id = body.get("client_id")
        imageUrls = body.get("imageUrls", [])  # Base64-encoded image URLs
        # Validate input
        assert (query or imageUrls) and client_id, "(use_camera or Query or Image) and client_id is required"
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body") from None
    except AssertionError:
        raise HTTPException(status_code=400, detail="Query or Image is required") from None

    async def start_identification(start_time: float, imageUrls: list[str]):
        # Call ChatGPT to identify the object
        chatgpt_response = None
        try:
            if os.environ.get("LLM_ENVIRONMENT") == "development":
                # Mock response for development
                chatgpt_response = ChatCompletion(
                    choices=[
                        Choice(
                            message=ChatCompletionMessage(
                                content=json.dumps(
                                    {
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
                                    }
                                ),
                                tokens=1452,
                                duration=7.048832893371582,
                                role="assistant",
                            ),
                            finish_reason="stop",
                            index=0,
                        )
                    ],
                    created=1700000000,
                    usage=CompletionUsage(prompt_tokens=100, completion_tokens=1352, total_tokens=1452),
                    id="chatcmpl-1234567890abcdef",
                    model="gpt-4o-mini",
                    object="chat.completion",
                )
                raise MockResponseException("Development mode: Mock response used for testing")

            chatgpt_response = get_bs(request).llm_completion.identify_object(query, imageUrls)
            if (
                not chatgpt_response
                or not chatgpt_response.choices
                or not chatgpt_response.choices[0].message
                or not chatgpt_response.choices[0].message.content
            ):
                raise EmptyResponseException()
        except (openai.APIConnectionError, EmptyResponseException, Exception) as e:
            sse_message = SseMessage(
                data=SseMessage.SseMessageData(
                    data={"message": str(e)}, reader_id=client_id, rfid="", duration=time.time() - start_time
                ).model_dump(mode="json"),
                event=Event.ERROR,
            )
            await get_bs(request).append_message_to_queue(client_id, sse_message)
            return
        except MockResponseException as e:
            print(e)
            pass

        result = json.loads(chatgpt_response.choices.pop(0).message.content)
        if imageUrls:
            result.setdefault("images", []).extend(imageUrls)
        sse_message = SseMessage(
            data=SseMessage.SseMessageData(
                reader_id=client_id,
                data={
                    "response": {
                        **result,
                    },
                    "tokens": chatgpt_response.usage.total_tokens,
                    "duration": time.time() - start_time,
                },
            ).model_dump(mode="json"),
            event=Event.COMPLETION,
        )
        await get_bs(request).append_message_to_queue(client_id, sse_message)

    asyncio.create_task(start_identification(time.time(), imageUrls))
    return {"message": "Identification process started"}
