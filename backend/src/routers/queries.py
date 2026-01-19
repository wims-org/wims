from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel

from db.db_queries import create_query, delete_query, get_all_queries, get_query_by_name, update_query
from routers.utils import get_db

router = APIRouter(prefix="/queries", tags=["Queries"])


class Query(BaseModel):
    name: str
    query: dict
    description: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


@router.post("", response_model=None)
async def create_query(request: Request, query: Query) -> Response | dict:
    """
    Create a query
    """
    db = get_db(request)
    existing_query = get_query_by_name(query.name, db)
    if existing_query:
        raise HTTPException(status_code=400, detail="Query with this name already exists.")
    created_query = create_query(query, db)
    return created_query


@router.get("/{name}", response_model=None)
async def get_query(request: Request, name: str) -> Response | dict:
    """
    Get a single query
    """
    db = get_db(request)
    query = get_query_by_name(name, db)
    if not query:
        raise HTTPException(status_code=404, detail="Query not found.")
    return query


@router.get("", response_model=None)
async def list_queries(request: Request) -> Response | list[Query]:
    """
    List all queries
    """
    db = get_db(request)
    queries = get_all_queries(db)
    return queries


@router.put("/{id}", response_model=None)
async def update_query(request: Request, id: str, query: Query) -> Response | dict:
    """
    Update a single query
    """
    db = get_db(request)
    updated_query = update_query(id, query, db)
    if not updated_query:
        raise HTTPException(status_code=404, detail="Query not found.")
    return updated_query


@router.delete("/{name}")
async def delete_query(request: Request, name: str):
    """
    Delete a singe query
    """
    db = get_db(request)
    deleted = delete_query(name, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Query not found.")
    return {"detail": "Query deleted successfully."}
