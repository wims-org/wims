from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

from database_connector import MongoDBConnector
from db import db_users
from models.database import User

router = APIRouter(
    prefix="/users", tags=["users"], responses={404: {"description": "Not found"}})


class UserRequest(BaseModel):
    username: str = Field(validate_default=True, min_length=3, max_length=50)
    tag_uuids: list[str] = Field(default_factory=list)
    email: str | None = None
    date_created: str | datetime = Field(default_factory=datetime.now)


def get_db(request: Request) -> MongoDBConnector:
    return request.app.state.backend_service.db


@router.post("", response_model=User)
async def create_user(request: Request, user: UserRequest) -> Response | dict:
    db = get_db(request).db
    existing_user = db_users.get_user_by_name(user.username, db)
    if existing_user:
        raise HTTPException(
            status_code=400, detail="User with this name already exists.")
    created_user = db_users.create_user(user, db)
    return created_user


@router.get("/{id}", response_model=User)
async def get_user(request: Request, id: str) -> Response | dict:
    db = get_db(request).db
    user = db_users.get_user_by_id(id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.get("", response_model=list[User])
async def get_all_users(request: Request, term: str | None = None) -> Response | list[User]:
    db = get_db(request).db
    if not term:
        users = db_users.get_all_users(db)
        return users
    query = {"$or": [{"username": {"$regex": term, "$options": "i"}},
                     {"email": {"$regex": term, "$options": "i"}}]}
    users = db_users.search_users(db, query)
    return users


@router.put("/{id}", response_model=User)
async def update_user(request: Request, id: str, user: User) -> Response | dict:
    db = get_db(request).db
    updated_user = db_users.update_user(id, user, db)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return updated_user


@router.delete("/{id}")
async def delete_user(request: Request, id: str):
    db = get_db(request).db
    deleted = db_users.delete_user(id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"detail": "User deleted successfully."}
