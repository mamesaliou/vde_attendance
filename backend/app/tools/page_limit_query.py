from typing import Optional


def page_limit_query(query, limit: Optional[int], page: int = 0):
    if page and limit:
        query = query.offset(page * limit).limit(limit)
    elif limit:
        query = query.limit(limit)
    return query