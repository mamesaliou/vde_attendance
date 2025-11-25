from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer, HTTPBearer, HTTPBasic
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp
from app.core.config import get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/app/token",
    scheme_name="OAuth2",
    description="Bearer token authentication",
    auto_error=True,
    scopes={
        "me": "Read information about the current user.",
        "teams": "Read and write access to teams.",
        "players": "Read and write access to players."
    }
)

security = HTTPBearer(
    scheme_name="Bearer",
    description="Enter your Bearer token",
    auto_error=True,
)

security_basic_auth = HTTPBasic(
    scheme_name="Basic",
    description="Basic app using username and password",
    auto_error=True
)

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        self.settings = get_settings()
        super().__init__(app)

    async def dispatch(self, request, call_next):
        if not request.url.scheme == "https" and not self.settings.DEBUG:
            return Response(
                status_code=status.HTTP_301_MOVED_PERMANENTLY,
                headers={"Location": str(request.url).replace("http://", "https://", 1)}
            )

        response = await call_next(request)

        if not self.settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE"
            
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        return response

async def verify_api_key(api_key: str = Security(api_key_header)) -> bool:
    settings = get_settings()
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    return True
