import pydantic
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from pydantic import BaseModel

from dependencies.backend_service import Event, SseMessage
from models.database import Item

router = APIRouter(prefix="/scan", responses={404: {"description": "Not found"}})


class ScanRequest(BaseModel):
    reader_id: str
    tag_id: str


class ScanResponse(BaseModel):
    msg: str
    item_name: str
    item_storage_location: str


@router.post("", response_model=ScanResponse)
async def scan_event(request: Request, body: ScanRequest) -> ScanResponse:
    logger.debug(f"Scan event from '{body.reader_id}' with tag '{body.tag_id}'")

    await request.app.state.backend_service.append_message_to_all_queues_with_reader(
        reader=body.reader_id,
        message=SseMessage(
            data=SseMessage.SseMessageData(reader_id=body.reader_id, rfid=body.tag_id), event=Event.SCAN
        ),
    )
    # Send db data to reader
    # todo don't fetch data from db twice
    item_raw = request.app.state.backend_service.db.find_by_rfid("items", body.tag_id)
    if item_raw:
        try:
            item = Item.model_validate(item_raw, strict=False, from_attributes=True)
            location = "---"
            if item.container:
                location = item.container.short_name
            return ScanResponse(msg="Found", item_name=item.short_name, item_storage_location=location)
        except pydantic.ValidationError as e:
            logger.error(f"Error validating item: {e}")
            # self.mqtt_client_manager.publish(self.item_data_topic + f"/{request.reader_id}", "ValidationError")
            raise HTTPException(status_code=400, detail="Validation error") from None
    else:
        # Item not found
        # self.mqtt_client_manager.publish(self.item_data_topic + f"/{request.reader_id}", "null")
        raise HTTPException(status_code=404, detail="Item not found")
