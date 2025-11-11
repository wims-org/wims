import json

from fastapi import APIRouter, HTTPException, Request, UploadFile

from routers.utils import get_bs

router = APIRouter(prefix="/backup", tags=["backup"], responses={404: {"description": "Not found"}})


@router.get("/create")
async def create_backup(request: Request):
    db = get_bs(request).dbc.db

    items = list(db.items.find())
    for i in items:
        i["_id"] = str(i["_id"])

    users = list(db.users.find())
    for u in users:
        u["_id"] = str(u["_id"])

    categories = list(db.categories.find())
    for c in categories:
        c["_id"] = str(c["_id"])

    readers = list(db.readers.find())
    for r in readers:
        r["_id"] = str(r["_id"])

    return {"items": items, "users": users, "categories": categories, "readers": readers}


@router.post("/load")
async def import_backup(request: Request, file: UploadFile):
    db = get_bs(request).dbc.db

    items = list(db.items.find())
    users = list(db.users.find())
    readers = list(db.readers.find())

    if len(items) + len(users) + len(readers) > 0:
        raise HTTPException(status_code=400, detail="Import only works on a completly empty DB")

    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    content = await file.read()

    data = json.loads(content)

    imported_items = 0
    imported_users = 0
    imported_readers = 0
    imported_categories = 0

    if len(data.get("items", [])):
        col = db["items"]
        x = col.insert_many(data["items"])
        imported_items = len(x.inserted_ids)

    if len(data.get("users", [])):
        col = db["users"]
        x = col.insert_many(data["users"])
        imported_users = len(x.inserted_ids)

    if len(data.get("categories", [])):
        col = db["categories"]
        x = col.insert_many(data["categories"])
        imported_categories = len(x.inserted_ids)

    if len(data.get("readers", [])):
        col = db["readers"]
        x = col.insert_many(data["readers"])
        imported_readers = len(x.inserted_ids)

    return (
        f"Correctly imported {imported_items} items, {imported_users} users,"
        f"{imported_categories} categories and {imported_readers} readers"
    )
