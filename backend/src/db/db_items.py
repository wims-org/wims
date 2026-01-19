from pymongo.database import Database

from models.database import Item
from models.requests import AggregatedStates, SearchQuery


def get_items_with_search_query(query: SearchQuery, db: Database) -> list[Item]:
    """Builds a MongoDB query from a SearchQuery object and returns matching items."""
    term_query = {
        "$or": [
            {"tag_uuid": {"$regex": query.term, "$options": "i"}},
            {"short_name": {"$regex": query.term, "$options": "i"}},
            {"description": {"$regex": query.term, "$options": "i"}},
            {"item_type": {"$regex": query.term, "$options": "i"}},
            {"tags": {"$regex": query.term, "$options": "i"}},
            {"manufacturer": {"$regex": query.term, "$options": "i"}},
        ]
    }
    if query.term and query.query:
        query.query.update(term_query)
    elif query.term:
        query.query = term_query

    # Build aggregation pipeline with deterministic ordering:
    # 1) $match
    # 2) single $sort (based on requested states or default)
    # 3) $skip
    # 4) $limit
    aggregations: list[dict] = []

    aggregations.append({"$match": query.query or {}})

    sort_spec: dict = {}
    for state in query.states or []:
        if state == AggregatedStates.borrowed:
            query.query.update({"borrowed_by": {"$regex": ".+"}})
        if state == AggregatedStates.todo:
            query.query.update({"tags": {"$in": ["review"]}})
        if state == AggregatedStates.empty:
            query.query.update({"$expr": {"$lt": ["$amount", "$minimum_amount"]}})

        if state == AggregatedStates.latest:
            sort_spec = {"created_at": -1}
        elif state == AggregatedStates.name_asc:
            sort_spec = {"short_name": 1}
        elif state == AggregatedStates.name_desc:
            sort_spec = {"short_name": -1}

    if not sort_spec:
        sort_spec = {"created_at": -1}

    aggregations.append({"$sort": sort_spec})
    aggregations.append({"$skip": query.offset or 0})
    aggregations.append({"$limit": query.limit or 1000})

    items = db["items"].aggregate(aggregations)

    return [Item.model_validate(item, strict=False, from_attributes=True) for item in items]
