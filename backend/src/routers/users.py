from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from dependencies import database
from models.user import User, UserCreate, UserPublic, UserUpdate

router = APIRouter(prefix="/users", tags=["users"], responses={404: {"description": "Not found"}})


@router.post("", response_model=UserPublic)
async def create_user(
    user: UserCreate,
    session: Annotated[AsyncSession, Depends(database.get_db_session)],
):
    db_user = User.model_validate(user)
    session.add(db_user)
    try:
        await session.commit()
    except IntegrityError as e:
        logger.warning(f"Attempt to create user with existing email: {user.email}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    await session.refresh(db_user)
    return db_user


@router.get("/{id}", response_model=UserPublic)
async def get_user(id: int, session: Annotated[AsyncSession, Depends(database.get_db_session)]):
    user = await session.get(User, id)
    if not user:
        raise HTTPException(status_code=400, detail="User id not found")
    return user


@router.get("", response_model=list[UserPublic])
async def get_all_users(
    session: Annotated[AsyncSession, Depends(database.get_db_session)], offset: int = 0, limit: int = 100
):
    return (await session.execute(select(User).offset(offset).limit(limit))).scalars().all()


@router.put("/{id}", response_model=UserPublic)
async def update_user(id: int, user: UserUpdate, session: Annotated[AsyncSession, Depends(database.get_db_session)]):
    db_user = await session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.delete("/{id}")
async def delete_user(id: int, session: Annotated[AsyncSession, Depends(database.get_db_session)]):
    user = await session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    await session.commit()
    return {"ok": True}
