from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user import EmailAlreadyExistsError, UserCRUD
from dependencies import database
from models.api.user import UserCreate, UserUpdate
from models.database.user import User

router = APIRouter(
    prefix="/users", tags=["users"], responses={404: {"description": "Not found"}})


@router.post("", response_model=User)
async def create_user(
    user: UserCreate,
    session: Annotated[AsyncSession, Depends(database.get_db_session)],
) -> User:
    try:
        return await UserCRUD(db=session).create(user)
    except EmailAlreadyExistsError as e:
        logger.warning(
            f"Attempt to create user with existing email: {user.email}")
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/{id}", response_model=User)
async def get_user(id: str, session: Annotated[AsyncSession, Depends(database.get_db_session)]) -> User:
    return await UserCRUD(db=session).find(id)


@router.get("", response_model=list[User])
async def get_all_users(
    session: Annotated[AsyncSession, Depends(database.get_db_session)],
) -> list[User]:
    return await UserCRUD(db=session).find_all()


@router.put("/{id}", response_model=User)
async def update_user(id: str,
                      payload: UserUpdate,
                      session: Annotated[AsyncSession, Depends(database.get_db_session)]) -> User:
    user = await UserCRUD(db=session).find(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await UserCRUD(db=session).update(user, payload)


@router.delete("/{id}")
async def delete_user(id: str, session: Annotated[AsyncSession, Depends(database.get_db_session)]):
    return await UserCRUD(db=session).delete(id)
