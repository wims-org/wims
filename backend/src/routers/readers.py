from fastapi import APIRouter

router = APIRouter(prefix="/readers", tags=["readers"], responses={404: {"description": "Not found"}})


@router.get("/")
async def get_readers():
    return [{"reader_id": "04-04-46-42-CD-66-81", "reader_name": "Reader 1"}, {"reader_id": "04-04-46-42-CD-66-82", "reader_name": "Reader 2"}]


@router.get("/{reader_id}", tags=["readers"])
async def read_user(reader_id: str):
    return {"reader_id": reader_id}
