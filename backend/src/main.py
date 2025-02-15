import asyncio
import base64
import json
import logging
import time
from contextlib import asynccontextmanager
from typing import Annotated

import pymongo
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Json, ValidationError
from sse_starlette.sse import EventSourceResponse

from dependencies.backend_service import MESSAGE_STREAM_DELAY, BackendService, Event, SseMessage
from dependencies.config import read_config
from models.database import Item
from models.requests import ItemRequest
from routers import readers
from utils import find

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)

logger.debug("Starting backend service")

global config

config = read_config()


def setup_middleware(
    app,
):
    frontend_config = config.get("frontend", {})
    origins = [
        "http://localhost:5000",
        "http://localhost:5002",
        "http://localhost:5005",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost",
        "https://localhost",
        "http://localhost:8080",
    ]
    origins.append(
        f"http://{frontend_config.get("host",
                                      "0.0.0.0")}:{frontend_config.get("port", '8080')}"
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.config = config
    app.state.backend_service = BackendService(
        db_config=config.get("database", {}),
        mqtt_config=config.get("mqtt", {}),
        config=config,
    )
    app.state.backend_service.start_mqtt()
    try:
        scan_topic = find(key := "mqtt.topics.scan", config)
    except (KeyError, TypeError) as e:
        logger.error(
            f"Error updating config key {
                key}, check config file and environment variables: {e}"
        )
    app.state.backend_service.add_mqtt_topic(scan_topic or "rfid/scan")
    yield
    app.state.backend_service.close()


app = FastAPI(lifespan=lifespan)
app.include_router(readers.router)
setup_middleware(app)


async def handle_message(message, topic):
    logger.debug(f"Handle message: {message} on topic {topic}")
    # await app.state.backend_service.websocket_manager.send_message(message, topic)


@app.get("/test-db")
async def test_db_connection():
    try:
        app.state.backend_service.db.connect()
        app.state.backend_service.db.disconnect()
        return {"message": "Database connection successful"}
    except Exception as e:
        return {"message": f"Database connection failed: {e}"}


# Routes


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


# Database Proxy


@app.put("/item/{rfid}")
async def put_item(request: Request):
    # update item
    item = await request.json()
    item_data = ItemRequest.model_validate(
        item, strict=False, from_attributes=True)
    item_data = Item.model_validate(
        item_data, strict=False, from_attributes=True)
    # item_data = item.model_dump(mode="json")
    updated_rows = app.state.backend_service.db.update(
        collection_name="items",
        # match by either tag_uuid or old container_tag_uuid, only for id migration
        query={"$or": [{"tag_uuid": item_data.tag_uuid}]},
        update_values=item_data.model_dump(mode="json", by_alias=True),
    )
    if updated_rows:
        return {"message": "Item updated successfully"}
    else:
        return {"message": "Failed to update item"}


@app.post("/item")
async def post_item(request: Request):
    # create item
    item = await request.json()
    item = {k: v for k, v in item.items() if v is not None}
    item_data = ItemRequest.model_validate(
        item, strict=False, from_attributes=True)
    item = Item.model_validate(item_data, strict=False, from_attributes=True)
    try:
        updated_rows = app.state.backend_service.db.create(
            collection_name="items",
            document=item.model_dump(mode="json", by_alias=True),
        )
    except pymongo.errors.DuplicateKeyError as e:
        raise HTTPException(
            status_code=400, detail="Item already exists") from e
    if updated_rows:
        logger.debug(f"Item created: {item_data}, {updated_rows}")
        return {"message": "Item created successfully"}
    else:
        return {"message": "Failed to update item"}


@app.delete("/item/{rfid}")
async def delete_item(rfid: str):
    updated_rows = app.state.backend_service.db.delete(
        collection_name="items",
        query={"tag_uuid": rfid},
    )
    if updated_rows:
        return {"message": "Item deleted successfully"}
    else:
        return {"message": "Failed to update item"}


@app.get("/item/{rfid}")
async def get_item(rfid: str):
    item = app.state.backend_service.db.find_by_rfid(
        collection_name="items", rfid=rfid)
    if item:
        try:
            return Item.model_validate(item, strict=False, from_attributes=True)
        except ValidationError as e:
            logger.error(f"Error validating item: {item=}, {e}")
            errors = [
                f"{'.'.join(err.get('loc', []))} {err.get('type')}: {err.get('msg')}" for err in e.errors()]
            valid_item = Item.model_construct(**item)
            res = valid_item.model_dump(
                exclude_unset=True, exclude_defaults=True, exclude_none=True)
            res["errors"] = errors
            return res

    else:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/items")
async def get_items(query: str = None):
    if query:
        items = app.state.backend_service.db.read(
            collection_name="items",
            query={
                "$or": [
                    {"tag_uuid": {"$regex": query, "$options": "i"}},
                    {"short_name": {"$regex": query, "$options": "i"}},
                    {"item_type": {"$regex": query, "$options": "i"}},
                    {"tags": {"$regex": query, "$options": "i"}},
                    {"manufacturer": {"$regex": query, "$options": "i"}},
                ]
            },
        )
    else:
        items = app.state.backend_service.db.read(collection_name="items")

    if items:
        return items
    else:
        return {"message": "Item not found"}


# dont look to closely at this


@app.patch("/items")
async def patch_items():
    items = app.state.backend_service.db.read(collection_name="items")
    for item_data in items:
        item = Item.model_validate(
            item_data, strict=False, from_attributes=True)
        item_data = item.model_dump(mode="json")
        _ = app.state.backend_service.db.update(
            collection_name="items",
            query={"container_tag_uuid": item_data["container_tag_uuid"]},
            update_values=item_data,
        )
    if items:
        return items
    else:
        return {"message": "Item not found"}


@app.post("/object-identification")
async def identify_item(request: Request, file: Annotated[bytes, File()]):
    photo = file
    query_params = dict(request.query_params)
    if "reader_id" not in query_params and "client_id" not in query_params:
        raise HTTPException(
            status_code=400, detail="Missing reader_id or client_id")
    sse_client = query_params.get("reader_id", query_params.get("client_id"))

    async def start_identification(start_time: float):
        chatgpt_response = await app.state.backend_service.llm_completion.identify_object(photo)
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
            app.state.backend_service.readers.setdefault(
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
        app.state.backend_service.readers.setdefault(
            sse_client, []).append(sse_message)

    asyncio.create_task(start_identification(time.time()))
    return {"message": "Identification process started"}


class IdentificationRequest(BaseModel):
    data: Json | None = None
    images: list[UploadFile] = None


@app.post("/identification")
async def identification(
    # identificationRequest: IdentificationRequest):
    data: Json = Form(...),
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

    async def start_identification(start_time: float):
        chatgpt_response = app.state.backend_service.llm_completion.identify_object(
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
            app.state.backend_service.readers.setdefault(
                client_id, []).append(sse_message)
            return
        logger.debug(f"ChatGPT response: {chatgpt_response}")
        sse_message = SseMessage(
            data=SseMessage.SseMessageData(
                reader_id=client_id, rfid=chatgpt_response, duration=time.time() - start_time
            ).model_dump(mode="json"),
            event=Event.COMPLETION,
        ).model_dump(mode="json")
        app.state.backend_service.readers.setdefault(
            client_id, []).append(sse_message)

    asyncio.create_task(start_identification(time.time()))
    return {"message": "Identification process started"}


def get_message():
    """this could be any function that blocks until data is ready"""
    time.sleep(1.0)
    s = time.ctime(time.time())
    return s


@app.get("/stream")
async def message_stream(request: Request, reader: str):
    logger.debug(f"Message stream{request}, {reader}")
    app.state.backend_service.readers[reader] = []

    def new_messages():
        return len(app.state.backend_service.readers[reader]) > 0

    async def event_generator():
        while True:
            # If client was closed the connection
            if await request.is_disconnected():
                break
            # Checks for new messages and return them to client if any
            if new_messages():
                message = app.state.backend_service.readers[reader].pop(0)
                if message["event"] != Event.ALIVE.value:
                    logger.debug(f"Sending message: {message}")
                yield message
            await asyncio.sleep(MESSAGE_STREAM_DELAY)

    return EventSourceResponse(event_generator())
