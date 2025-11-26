import time
from typing import Optional
from fastapi import Request, Response
from app.core.logging import get_logger

logger = get_logger(__name__)

async def request_logging_middleware(request: Request, call_next):
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", "N/A")
    logger.info(
        "request_started",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host,
        user_agent=request.headers.get("User-Agent", "N/A")
    )
    response: Optional[Response] = None
    try:
        response = await call_next(request)
        return response
    finally:
        duration = time.time() - start_time
        
        log_kwargs = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "duration": duration,
            "status_code": response.status_code if response else "N/A",
            "client_ip": request.client.host
        }
        
        if response and "content-length" in response.headers:
            log_kwargs["response_size"] = response.headers["content-length"]
            
        if response:
            if response.status_code >= 500:
                logger.error("request_finished", **log_kwargs)
            elif response.status_code >= 400:
                logger.warning("request_finished", **log_kwargs)
            else:
                logger.info("request_finished", **log_kwargs)
