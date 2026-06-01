import os
from hashlib import md5
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from dependencies import database
from dependencies.settings import SettingsDep
from models.api import WebhookEvent
from models.item import File, FilePublic, FileUpdate
from modules.webhook_handler import WebhookData, WebhookHandler

router = APIRouter(prefix="/files", tags=["files"], responses={404: {"description": "Not found"}})


@router.post("", response_model=FilePublic)
async def create_file(
    file: UploadFile, session: Annotated[AsyncSession, Depends(database.get_db_session)], settings: SettingsDep
):
    data = file.file.read()
    hash_name = md5(data).hexdigest() + "." + file.filename.split(".")[-1]
    asset_uri = os.path.join(settings.asset_uri_prefix, hash_name)
    fs_path: Path = Path(settings.data_path) / Path(hash_name)
    db_file = (await session.execute(select(File).where(File.uri == asset_uri))).scalar_one_or_none()
    if db_file:
        if not fs_path.exists():
            fs_path.write_bytes(data)
        return db_file

    fs_path.write_bytes(data)

    db_file = File(
        filename=file.filename,
        uri=asset_uri,
        filetype="image",
    )
    session.add(db_file)
    try:
        await session.commit()
    except IntegrityError as e:
        # Race condition: another request inserted the same file between our check and insert
        await session.rollback()
        db_file = (await session.execute(select(File).where(File.uri == asset_uri))).scalar_one_or_none()
        if not db_file:
            raise HTTPException(status_code=500, detail="Failed to create file and no existing file found") from e
        return db_file
    await session.refresh(db_file)
    WebhookHandler.send_webhook(WebhookData(event_type=WebhookEvent.FILE_CREATE, data=db_file))
    return db_file


@router.get("/{id}", response_model=FilePublic)
async def get_file(id: int, session: Annotated[AsyncSession, Depends(database.get_db_session)]):
    file = await session.get(File, id)
    if not file:
        raise HTTPException(status_code=400, detail="File id not found")
    return file


@router.get("", response_model=list[FilePublic])
async def get_all_files(
    session: Annotated[AsyncSession, Depends(database.get_db_session)], offset: int = 0, limit: int = 100
):
    return (await session.execute(select(File).offset(offset).limit(limit))).scalars().all()


@router.put("/{id}", response_model=FilePublic)
async def update_file(id: int, file: FileUpdate, session: Annotated[AsyncSession, Depends(database.get_db_session)]):
    db_file = await session.get(File, id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    file_data = file.model_dump(exclude_unset=True)
    db_file.sqlmodel_update(file_data)
    session.add(db_file)
    await session.commit()
    await session.refresh(db_file)
    WebhookHandler.send_webhook(WebhookData(event_type=WebhookEvent.FILE_UPDATE, data=db_file))
    return db_file


@router.delete("/{id}")
async def delete_file(id: str, session: Annotated[AsyncSession, Depends(database.get_db_session)]):
    db_file = await session.get(File, id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    session.delete(db_file)
    await session.commit()
    WebhookHandler.send_webhook(WebhookData(event_type=WebhookEvent.FILE_DELETE, data=db_file))
    return {"ok": True}
