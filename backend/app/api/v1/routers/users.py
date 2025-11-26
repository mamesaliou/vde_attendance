from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request

from app.api.v1.schemas.user import UserUpdate, UserResponse
from app.core.security import security
from app.core.decorators import require_superuser, handle_exceptions
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough permissions"}
    }
)

user_service = UserService()


@router.get("/me", response_model=UserResponse)
#@handle_exceptions
async def read_users_me(request: Request, token: str = Depends(security)) -> UserResponse:
    return await user_service.get_current_user(request.state.token_data["sub"])


@router.put("/me", response_model=UserResponse)
@handle_exceptions
@require_superuser()
async def update_user_me(request: Request, user_data: UserUpdate,
                         token: str = Depends(security),
                         invitation_code: Optional[str] = None) -> UserResponse:
    return await user_service.update_current_user(request.state.token_data["sub"], user_data)


@router.get("/{username_or_handle}", response_model=UserResponse)
@handle_exceptions
@require_superuser()
async def read_user(
    request: Request,
    username_or_handle: str,
    token: str = Depends(security)
) -> UserResponse:
    return await user_service.get_user_by_identifier(username_or_handle)


@router.get("", response_model=List[UserResponse])
@handle_exceptions
async def list_users(
    username: Optional[str] = Query(None, description="Filtrer par nom d'utilisateur"),
    handle: Optional[str] = Query(None, description="Filtrer par handle"),
    email: Optional[str] = Query(None, description="Filtrer par email"),
    is_active: Optional[bool] = Query(None, description="Filtrer par statut actif/inactif"),
    is_superuser: Optional[bool] = Query(None, description="Filtrer par rôle admin"),
    limit: int = Query(10, ge=1, le=100, description="Nombre d'éléments par page"),
    page: int = Query(0, ge=0, description="Numéro de la page"),
    token: str = Depends(security)
) -> List[UserResponse]:
    return await user_service.list_users(
        username=username,
        handle=handle,
        email=email,
        is_active=is_active,
        is_superuser=is_superuser,
        limit=limit,
        page=page
    )


@router.delete("/{user_id}")
@handle_exceptions
@require_superuser()
async def delete_user(
    user_id: int,
    token: str = Depends(security)
):
    return await user_service.delete_user(user_id)
