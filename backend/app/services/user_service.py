from typing import List, Optional
from sqlalchemy.exc import NoResultFound

from app.api.v1.schemas.user import UserUpdate, UserResponse, UserInDB
from app.core.exceptions import BadRequestError
from app.services.auth_service import AuthService
from app.services.database_services import DbService


class UserService:
    def __init__(self):
        self.auth_service = AuthService()
        self.db_service = DbService()

    async def get_user_from_token(self, token: str) -> UserInDB:
        # Décoder le token pour obtenir le nom d'utilisateur (sub)
        token_data = self.auth_service.decode_token(token)

        if not token_data.sub:
            raise ValueError("Invalid token: missing subject")

        # Récupérer l'utilisateur à partir du nom d'utilisateur
        try:
            return await self.get_current_user(username=token_data.sub)
        except Exception as e:
            raise ValueError(f"User not found: {str(e)}")

    async def get_current_user(self, username: str) -> UserResponse:
        return UserResponse.model_validate(
            await self.db_service.get_user_by_username(username)
        )

    async def update_current_user(self, username: str, user_data: UserUpdate) -> UserResponse:
        user = await self.db_service.get_user_by_username(username)

        # Vérifier les permissions pour la mise à jour du statut
        if not user.is_superuser and user_data.is_active:
            raise BadRequestError("Only superusers can update user status")

        # Mettre à jour l'utilisateur
        return UserResponse.model_validate(
            await self.db_service.update_user(user_id=user.id, **user_data.model_dump(exclude_none=True))
        )

    async def get_user_by_identifier(self, username_or_handle: str) -> UserResponse:
        try:
            return UserResponse.model_validate(
                await self.db_service.get_user_by_username(username_or_handle)
            )
        except NoResultFound:
            return UserResponse.model_validate(
                await self.db_service.get_user_by_handle(username_or_handle)
            )

    async def list_users(
            self,
            username: Optional[str] = None,
            handle: Optional[str] = None,
            email: Optional[str] = None,
            is_active: Optional[bool] = None,
            is_superuser: Optional[bool] = None,
            limit: int = 10,
            page: int = 0
    ) -> List[UserResponse]:

        filters = {}
        if username:
            filters["username"] = username
        if handle:
            filters["handle"] = handle
        if email:
            filters["email"] = email
        if is_active is not None:
            filters["is_active"] = is_active
        if is_superuser is not None:
            filters["is_superuser"] = is_superuser

        users = await self.db_service.list_users(limit=limit, page=page, **filters)
        return [UserResponse.model_validate(user) for user in users]

    async def delete_user(self, user_id: int):
        await self.db_service.delete_user(user_id)
        return {"status": "success", "message": f"User {user_id} deleted"}
