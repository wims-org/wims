from pymongo.database import Database

from models.database import Item
from models.requests import AggregatedStates, SearchQuery


def get_items_with_search_query(query: SearchQuery, db: Database) -> list[Item]:
    """Builds a MongoDB query from a SearchQuery object and returns matching items."""
    if query.term:
        query.query.update(
            {
                "$or": [
                    {"tag_uuid": {"$regex": query.term, "$options": "i"}},
                    {"short_name": {"$regex": query.term, "$options": "i"}},
                    {"description": {"$regex": query.term, "$options": "i"}},
                    {"item_type": {"$regex": query.term, "$options": "i"}},
                    {"tags": {"$regex": query.term, "$options": "i"}},
                    {"manufacturer": {"$regex": query.term, "$options": "i"}},
                ]
            }
        )
    for state in query.states or []:
        if state == AggregatedStates.borrowed:
            query.query.update({"borrowed_by": {"$regex": ".+"}})
        if state == AggregatedStates.todo:
            query.query.update({"tags": {"$in": ["review"]}})
        if state == AggregatedStates.empty:
            query.query.update({"$expr": {"$lt": ["$amount", "$minimum_amount"]}})

    items = db["items"].aggregate(
        [
            {"$match": query.query or {}},
            {"$skip": query.offset or 0},
            {"$limit": query.limit or 1000},
            {"$sort": {"created_at": -1}},
        ]
    )

    return [Item.model_validate(item, strict=False, from_attributes=True) for item in items]
