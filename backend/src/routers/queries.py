from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel

from db.db_queries import create_query, delete_query, get_all_queries, get_query_by_name, update_query
from routers.utils import get_bs

router = APIRouter(prefix="/queries", tags=["queries"])


# Pydantic model for Query
class Query(BaseModel):
    name: str
    query: dict
    description: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


@router.post("", response_model=None)
async def create_query_endpoint(request: Request, query: Query) -> Response | dict:
    db = get_bs(request).dbc.db
    existing_query = get_query_by_name(query.name, db)
    if existing_query:
        raise HTTPException(status_code=400, detail="Query with this name already exists.")
    created_query = create_query(query, db)
    return created_query


@router.get("/{name}", response_model=None)
async def get_query_endpoint(request: Request, name: str) -> Response | dict:
    db = get_bs(request).dbc.db
    query = get_query_by_name(name, db)
    if not query:
        raise HTTPException(status_code=404, detail="Query not found.")
    return query


@router.get("", response_model=None)
async def get_all_queries_endpoint(request: Request) -> Response | list[Query]:
    db = get_bs(request).dbc.db
    queries = get_all_queries(db)
    return queries


@router.put("/{id}", response_model=None)
async def update_query_endpoint(request: Request, id: str, query: Query) -> Response | dict:
    db = get_bs(request).dbc.db
    updated_query = update_query(id, query, db)
    if not updated_query:
        raise HTTPException(status_code=404, detail="Query not found.")
    return updated_query


@router.delete("/{name}")
async def delete_query_endpoint(request: Request, name: str):
    db = get_bs(request).dbc.db
    deleted = delete_query(name, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Query not found.")
    return {"detail": "Query deleted successfully."}
