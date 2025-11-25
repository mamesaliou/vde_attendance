from fastapi import APIRouter, Depends, status, Request
from fastapi.security import HTTPBasicCredentials
from app.api.v1.schemas.auth import Token, User, UserCreate
from app.api.v1.schemas.invitation_code import InvitationCodeCreate, InvitationCodeResponse
from app.core.exceptions import BadRequestError, UnauthorizedError
from app.services.auth_service import AuthService
from app.services.secret_service import secret_service
from app.core.security import security, security_basic_auth
from app.core.decorators import require_superuser, handle_exceptions

router = APIRouter()

@router.get("/public-key")
@handle_exceptions
async def get_public_key():
    try:
        secret_service.generate_keys_if_missing()
        return {
            "public_key": secret_service.get_public_key_pem(),
            "algorithm": "RS256",
            "key_type": "RSA",
            "usage": "JWT signature verification"
        }
    except Exception as e:
        raise BadRequestError(message=f"Erreur récupération clé publique: {str(e)}")

@router.post("/token", response_model=Token)
@handle_exceptions
async def login_for_access_token(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(security_basic_auth),
    auth_service: AuthService = Depends(),
):
    user = await auth_service.authenticate_user(credentials.username, credentials.password)
    if not user:
        raise BadRequestError(
            message="Incorrect username or password"
        )

    data = {
        "sub": user.username,
        "is_superuser": user.is_superuser
    }
    access_token, payload = await auth_service.create_jwt_token(payload=data, audience=request.state.audience)
    r_token, payload = await auth_service.create_refresh_token(data=data, audience=request.state.audience)
    return {
        "access_token": access_token,
        "refresh_token": r_token,
        "token_type": "bearer",
        "expires_at": payload["exp"]
    }


@router.post("/refresh", response_model=Token)
@handle_exceptions
@require_superuser()
async def refresh_token(
    request: Request,
    token: str = Depends(security),
    auth_service: AuthService = Depends()
):
    return await auth_service.refresh_access_token(
        request.state.token_data,
        audience=request.state.audience
    )

@router.post("/register", response_model=User)
@handle_exceptions
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends()
):
    return await auth_service.register_user(user_data)

@router.post("/verify", status_code=status.HTTP_200_OK)
@handle_exceptions
async def verify_token(
    request: Request,
    token: str = Depends(security),
):
    payload = request.state.token_data
    if not payload:
        raise UnauthorizedError(
            message="Token invalide ou expiré"
        )
    return {"status": "valid", "token": token.credentials, "payload": payload}


@router.post("/invitation-codes", response_model=InvitationCodeResponse)
@handle_exceptions
@require_superuser()
async def create_invitation_code(
        request: Request,
        data: InvitationCodeCreate,
        token: str = Depends(security),
        auth_service: AuthService = Depends()
):
    invitation = await auth_service.create_invitation_code(
        created_by=request.state.token_data["sub"],
        expires_in_days=data.expires_in_days,
        is_superuser=data.is_superuser
    )

    return invitation

@router.post("/logout")
@handle_exceptions
async def logout(
    request: Request,
    token: str = Depends(security),
    auth_service: AuthService = Depends()
):
    payload = request.state.token_data
    await auth_service.revoke_token(payload.get("jti"))
    return {"message": "Successfully logged out"}
