from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from pydantic import BaseModel

from routers.utils import get_bs

router = APIRouter(prefix="/readers", tags=["readers"], responses={404: {"description": "Not found"}})


class Reader(BaseModel):
    reader_id: str
    reader_name: str


@router.get("", response_model=list[Reader])
async def get_readers(request: Request):
    logger.debug("Fetching all readers")
    readers = list(get_bs(request).db.read("readers"))
    return readers


@router.get("/{reader_id}", response_model=Reader)
async def read_user(request: Request, reader_id: str):
    reader = get_bs(request).db.read("readers", {"reader_id": reader_id})
    if reader is None:
        raise HTTPException(status_code=404, detail="Reader not found")
    return reader


@router.post("", response_model=Reader)
async def create_reader(request: Request, reader: Reader):
    res = get_bs(request).db.create("readers", reader.model_dump(mode="dict"))
    return reader if res else None


@router.delete("/{reader_id}", response_model=dict)
async def delete_reader(request: Request, reader_id: str):
    result = get_bs(request).db.delete("readers", {"reader_id": reader_id})
    if result == 0:
        raise HTTPException(status_code=404, detail="Reader not found")
    return {"message": "Reader deleted successfully"}
