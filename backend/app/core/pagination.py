from typing import TypeVar, Generic, List, Optional
from fastapi import Request
from pydantic import BaseModel, ConfigDict
from math import ceil

T = TypeVar('T')

class Page(BaseModel, Generic[T]):

    items: List[T]
    total: int
    page: int
    limit: int
    pages: int
    links: Optional[dict] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

def paginate(
    items: List[T],
    page: int,
    limit: int,
    request: Request
) -> Page[T]:
    total = len(items)
    pages = ceil(total / limit)
    
    base_url = str(request.url)
    if "?" in base_url:
        base_url = base_url.split("?")[0]
    
    links = {
        "first": f"{base_url}?page=0&limit={limit}"
    }
    
    if pages > 1:
        links["last"] = f"{base_url}?page={pages - 1}&limit={limit}"
    
    if page < pages - 1:
        links["next"] = f"{base_url}?page={page + 1}&limit={limit}"
    
    if page > 0:
        links["prev"] = f"{base_url}?page={page - 1}&limit={limit}"
    
    headers = {
        "X-Total-Count": str(total),
        "X-Page": str(page),
        "X-Pages": str(pages),
        "X-Limit": str(limit),
        "Link": []
    }
    
    for rel, url in links.items():
        headers["Link"].append(f'<{url}>; rel="{rel}"')
    
    headers["Link"] = ", ".join(headers["Link"])
    request.state.pagination_headers = headers
    
    return Page(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
        links=links
    )

def paginated_response(func):
    async def wrapper(*args, **kwargs):
        request = None
        page = 0
        limit = 5
        
        for arg in args:
            if isinstance(arg, Request):
                request = arg
        
        if "request" in kwargs:
            request = kwargs["request"]
        if "page" in kwargs:
            page = kwargs["page"]
        if "limit" in kwargs:
            limit = kwargs["limit"]
        
        if not request:
            raise ValueError("Le décorateur paginated_response nécessite Request")
        
        items = await func(*args, **kwargs)
        
        page_response = paginate(items, page, limit, request)
        
        return page_response
    
    return wrapper
