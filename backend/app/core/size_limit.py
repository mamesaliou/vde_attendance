from typing import Optional
from fastapi import Request, HTTPException, status
from app.core.logging import get_logger

logger = get_logger(__name__)

class RequestSizeLimiter:
    def __init__(
        self,
        max_body_size: int = 1024 * 1024,  # 1 MB par défaut
        max_file_size: int = 5 * 1024 * 1024,  # 5 MB par défaut
    ):
        self.max_body_size = max_body_size
        self.max_file_size = max_file_size
    
    async def check_body_size(self, request: Request) -> Optional[int]:
        if request.headers.get("content-length"):
            content_length = int(request.headers["content-length"])
            if content_length > self.max_body_size:
                logger.warning(
                    "request_body_too_large",
                    size=content_length,
                    limit=self.max_body_size,
                    path=request.url.path,
                    client_ip=request.client.host
                )
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail={
                        "message": "Le corps de la requête est trop grand",
                        "max_size": f"{self.max_body_size / 1024 / 1024:.1f}MB",
                        "received_size": f"{content_length / 1024 / 1024:.1f}MB"
                    }
                )
            return content_length
        return None

    async def check_file_size(self, request: Request):
        if request.headers.get("content-type", "").startswith("multipart/form-data"):
            form = await request.form()
            for field in form:
                if hasattr(form[field], "file"):
                    # C'est un fichier
                    file = form[field]
                    content = await file.read()
                    if len(content) > self.max_file_size:
                        logger.warning(
                            "uploaded_file_too_large",
                            filename=file.filename,
                            size=len(content),
                            limit=self.max_file_size,
                            path=request.url.path,
                            client_ip=request.client.host
                        )
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail={
                                "message": "Le fichier uploadé est trop grand",
                                "filename": file.filename,
                                "max_size": f"{self.max_file_size / 1024 / 1024:.1f}MB",
                                "received_size": f"{len(content) / 1024 / 1024:.1f}MB"
                            }
                        )
                    await file.seek(0)

_size_limiter = RequestSizeLimiter()

async def request_size_middleware(request: Request, call_next):
    await _size_limiter.check_body_size(request)
    await _size_limiter.check_file_size(request)
    return await call_next(request)
