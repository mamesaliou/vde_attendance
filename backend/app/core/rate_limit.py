import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, Deque
from fastapi import Request, HTTPException, status
from app.core.logging import get_logger

logger = get_logger(__name__)

@dataclass
class RateLimitConfig:
    requests_per_minute: int = 60
    window_size: int = 60  # en secondes

class InMemoryRateLimiter:

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self._requests: Dict[str, Deque[float]] = defaultdict(lambda: deque())
    
    def _clean_old_requests(self, key: str, now: float):
        window_start = now - self.config.window_size
        
        while self._requests[key] and self._requests[key][0] < window_start:
            self._requests[key].popleft()
            
        if not self._requests[key]:
            del self._requests[key]
    
    def is_rate_limited(self, key: str) -> bool:
        now = time.time()
        self._clean_old_requests(key, now)
        if len(self._requests[key]) >= self.config.requests_per_minute:
            return True
            
        self._requests[key].append(now)
        return False

_rate_limiter = InMemoryRateLimiter(RateLimitConfig())

async def rate_limit_middleware(request: Request, call_next):
    key = f"rate_limit:{request.client.host}:{request.url.path}"
    
    if _rate_limiter.is_rate_limited(key):
        logger.warning(
            "rate_limit_exceeded",
            ip=request.client.host,
            path=request.url.path
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Trop de requêtes. Veuillez réessayer plus tard.",
                "retry_after": "60 seconds"
            }
        )
    
    return await call_next(request)
