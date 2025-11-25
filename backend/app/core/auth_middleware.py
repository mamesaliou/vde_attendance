from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.services.auth_service import AuthService

async def verify_token(request: Request, call_next):

    auth_service = AuthService()

    service_name = request.headers.get("X-Service-Name")
    path = request.url.path
    audience = service_name if service_name in settings.TRUSTED_SERVICES else settings.JWT_SERVER_AUDIENCE
    request.state.audience = audience
    auth_header = request.headers.get("Authorization")
    
    request.state.token_data = None
    
    if request.method == "OPTIONS":
        return await call_next(request)

    # if not auth_header and any(path.startswith(public_path) for public_path in settings.PUBLIC_ENDPOINTS):
    #     return await call_next(request)

    if any(path.startswith(public_path) for public_path in settings.PUBLIC_ENDPOINTS):
        return await call_next(request)

    if not settings.DEBUG:
        await auth_service.validate_service(service_name, request.headers.get("X-Request-ID"))

    if any(path.startswith(public_path) for public_path in settings.PUBLIC_INTERNAL_ENDPOINTS):
        return await call_next(request)

    try:
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Bearer token manquant ou invalide"}
            )
        
        token = auth_header.split(" ")[1]
        invitation_code = request.query_params.get("invitation_code")
        payload = await auth_service.verify_token(token, audience=audience, invitation_code=invitation_code)
        
        if not payload:
            return JSONResponse(
                status_code=401,
                content={
                    "detail": {
                        "error": {
                            "error_id": None,
                            "message": "Token invalide ou expiré",
                            "code": 401,
                            "details": "Le token fourni n'est pas valide ou a expiré"
                        }
                    }
                }
            )
        
        request.state.token_data = payload
        return await call_next(request)
        
    except Exception as e:
        return JSONResponse(
            status_code=401,
            content={"detail": str(e)}
        )
