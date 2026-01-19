from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

from db import db_users
from models.database import User
from routers.utils import get_db

router = APIRouter(prefix="/users", tags=["Users"])


class UserRequest(BaseModel):
    username: str = Field(validate_default=True, min_length=3, max_length=50)
    tag_uuids: list[str] = Field(default_factory=list)
    email: str | None = None
    date_created: str | datetime = Field(default_factory=datetime.now)


@router.post("", response_model=User)
async def create_user(request: Request, user: UserRequest) -> Response | dict:
    """
    Create a user
    """
    db = get_db(request)
    existing_user = db_users.get_user_by_name(user.username, db)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this name already exists.")
    created_user = db_users.create_user(user, db)
    return created_user


@router.get("/{id}", response_model=User)
async def get_user(request: Request, id: str) -> Response | dict:
    """
    Get a single user
    """
    db = get_db(request)
    user = db_users.get_user_by_id(id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.get("", response_model=list[User])
async def list_users(request: Request, term: str | None = None) -> Response | list[User]:
    """
    List all users
    """
    db = get_db(request)
    if not term:
        users = db_users.get_all_users(db)
        return users
    query = {"$or": [{"username": {"$regex": term, "$options": "i"}}, {"email": {"$regex": term, "$options": "i"}}]}
    users = db_users.search_users(db, query)
    return users

# TODO: Add /search


@router.put("/{id}", response_model=User)
async def update_user(request: Request, id: str, user: User) -> Response | dict:
    """
    Update a user
    """
    db = get_db(request)
    updated_user = db_users.update_user(id, user, db)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return updated_user


@router.delete("/{id}")
async def delete_user(request: Request, id: str):
    """
    Delete a user
    """
    db = get_db(request)
    deleted = db_users.delete_user(id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"detail": "User deleted successfully."}
