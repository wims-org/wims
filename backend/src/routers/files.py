from hashlib import md5
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile
from fastapi.exceptions import HTTPException
from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from dependencies import database
from dependencies.settings import SettingsDep
from models.item import File, FilePublic, FileUpdate

router = APIRouter(prefix="/files", tags=["files"], responses={404: {"description": "Not found"}})


@router.post("", response_model=FilePublic)
async def create_file(
    file: UploadFile, session: Annotated[AsyncSession, Depends(database.get_db_session)], settings: SettingsDep
):
    data = file.file.read()
    asset_path = md5(data).hexdigest() + "." + file.filename.split(".")[-1]
    asset_path: Path = settings.asset_path / asset_path
    asset_path.write_bytes(data)

    # Check if we already have a file with this hash.
    # e.g. from a failed
    db_file = await session.execute(select(File).where(File.asset_path == asset_path))
    db_file = db_file.scalar_one_or_none()
    if db_file:
        return db_file

    db_file = File(
        filename=file.filename,
        asset_path=str(asset_path),
        filetype="image",
    )
    session.add(db_file)
    try:
        await session.commit()
    except IntegrityError as e:
        logger.warning("Failed to create image")
        raise HTTPException(status_code=400, detail=str(e)) from e
    await session.refresh(db_file)
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
    return db_file


@router.delete("/{id}")
async def delete_file(id: str, session: Annotated[AsyncSession, Depends(database.get_db_session)]):
    file = await session.get(File, id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    session.delete(file)
    await session.commit()
    return {"ok": True}
