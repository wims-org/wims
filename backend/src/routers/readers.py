from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from routers.utils import get_bs

router = APIRouter(prefix="/readers", tags=["Readers"])


class Reader(BaseModel):
    reader_id: str
    reader_name: str


@router.get("", response_model=list[Reader])
async def list_readers(request: Request):
    """
    Get a list of all readers
    """
    readers = list(get_bs(request).dbc.read("readers"))
    return readers


@router.get("/{reader_id}", response_model=Reader)
async def get_reader(request: Request, reader_id: str):
    """
    Get a single reader
    """
    reader = get_bs(request).dbc.read("readers", {"reader_id": reader_id})
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    return reader[0]


@router.post("", response_model=Reader)
async def create_reader(request: Request, reader: Reader):
    """
    Create a new reader
    """
    res = get_bs(request).dbc.create("readers", reader.model_dump(mode="dict"))
    return reader if res else None


@router.delete("/{reader_id}", response_model=dict)
async def delete_reader(request: Request, reader_id: str):
    """
    Delete a reader
    """
    result = get_bs(request).dbc.delete("readers", {"reader_id": reader_id})
    if result == 0:
        raise HTTPException(status_code=404, detail="Reader not found")
    return {"message": "Reader deleted successfully"}
