import uuid
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

import jwt
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from passlib.context import CryptContext
from sqlalchemy.exc import NoResultFound
from datetime import timezone

from app.core.logging import get_logger

from app.core.config import settings
from app.core.exceptions import BadRequestError, ForbiddenError, UnauthorizedError
from app.services.database_services import DbService
from app.services.secret_service import SecretService

logger = get_logger(__name__)


class AuthService:
    def __init__(self):
        self.db_service = DbService()
        self.__secret_service = SecretService()
        # Utilisation des clés RSA pour RS256
        self.__secret_key = self.__secret_service.get_private_key_pem()
        self.__public_key = self.__secret_service.get_public_key_pem()
        self.__access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.__refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    async def validate_service(service_name: str, request_id: str) -> bool:
        trusted_service = service_name in settings.TRUSTED_SERVICES or (service_name or "").rstrip("/") in settings.TRUSTED_SERVICES
        if not trusted_service:
            raise ForbiddenError(f"Invalid service name: {service_name}")
        #if not RedisService().validate_request_id(service_name, request_id):
        #    raise ForbiddenError("Invalid service secret")
        return True

    async def verify_invitation_code(self, code: str) -> Optional[dict]:
        if not code:
            return None
        try:
            invitation = await self.db_service.get_invitation_code(code)
        except NoResultFound:
            return None
        now = datetime.utcnow()
        expires_at = invitation.expires_at.replace(tzinfo=None) if invitation.expires_at else None
        used_at = invitation.used_at.replace(tzinfo=None) if invitation.used_at else None

        if expires_at < now or used_at:
            return None

        return {
            "code": invitation.code,
            "expires_at": invitation.expires_at,
            "is_superuser": invitation.is_superuser
        }

    async def create_invitation_code(self, created_by: str, expires_in_days: int = 7,
                                     is_superuser: bool = False) -> dict:
        code = str(uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        invitation = await self.db_service.create_invitation_code(
            code=code,
            expires_at=expires_at,
            created_by=created_by,
            is_superuser=is_superuser
        )
        return {
            "code": invitation.code,
            "expires_at": invitation.expires_at,
            "is_superuser": invitation.is_superuser
        }

    async def register_user(self, user_data) -> dict:
        if not user_data.invitation_code and user_data.is_active:
            raise BadRequestError("Invitation code is required")
        try:
            existing_user = await self.db_service.get_unique_user(username=user_data.username,
                                                                  email=user_data.email,
                                                                  handle=user_data.handle)
            if existing_user:
                raise BadRequestError("Username already registered")
        except NoResultFound:
            pass

        is_superuser = False
        if user_data.invitation_code:
            invitation = await self.verify_invitation_code(user_data.invitation_code)
            if not invitation or (user_data.is_superuser and not invitation["is_superuser"]):
                raise BadRequestError("Invalid or expired invitation code")
            is_superuser = user_data.is_superuser

            await self.db_service.update_invitation_code(
                code=user_data.invitation_code,
                used_at=datetime.now(timezone.utc)
            )
        hashed_password = self.get_password_hash(user_data.password)
        user = await self.db_service.create_user(
            username=user_data.username,
            email=user_data.email,
            handle=user_data.handle,
            hashed_password=hashed_password,
            is_superuser=is_superuser
        )
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "handle": user.handle,
            "is_active": user.is_active,
            "is_superuser": is_superuser
        }

    async def create_access_token(self, data: dict, audience: Optional[str] = None) -> tuple[str, dict]:
        to_encode = data.copy()
        return await self.create_jwt_token(to_encode, is_refresh_token=False, audience=audience)

    async def create_refresh_token(self, data: dict, audience: str) -> tuple[str, dict]:
        to_encode = data.copy()
        token, payload = await self.create_jwt_token(to_encode, is_refresh_token=True, audience=audience)

        await self.db_service.create_revoked_token(
            jti=payload["jti"],
            expires_at=payload["expire"],
            revoked_by="",
            device_info=None
        )
        return token, payload

    async def create_jwt_token(self, payload: dict, audience: str, is_refresh_token: bool = False) -> tuple[str, dict]:
        try:
            payload['aud'] = audience

            payload['type'] = 'refresh' if is_refresh_token else 'access'

            now = datetime.now(timezone.utc)
            if is_refresh_token:
                expire = payload.pop("expire", now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
            else:
                expire = payload.pop("expire", now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
            payload['exp'] = payload.get('exp', int(expire.timestamp()))
            payload['iss'] = settings.JWT_ISSUER

            if is_refresh_token and 'jti' not in payload:
                payload['jti'] = str(uuid.uuid4())

            token = jwt.encode(
                payload=payload,
                key=self.__secret_key,
                algorithm=settings.JWT_ALGORITHM
            )
            payload["expire"] = expire
            logger.info(
                f"JWT token created for subject: {payload.get('sub')} and audience: {payload.get('aud', 'default')}")
            return token, payload.copy()
        except Exception as e:
            logger.error(f"JWT creation error: {e}")
            raise UnauthorizedError(f"Failed to create token: {e}")

    async def decode_jwt_token(self, token: str, audience: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                key=self.__public_key,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iss": True,
                    "verify_aud": True
                },
                issuer=settings.JWT_ISSUER,
                audience=audience,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except ExpiredSignatureError:
            logger.warning("JWT token expired")
            raise UnauthorizedError("Token has expired")
        except Exception as e:
            logger.error(f"JWT validation error: {e}")
            raise UnauthorizedError("Invalid token")

    async def verify_token(self, token: str, audience: str, invitation_code: Optional[str] = None) -> Optional[dict]:
        try:
            payload = await self.decode_jwt_token(token, audience=audience)

            exp = payload.get("exp")
            if exp is None or datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                return None

            try:
                user = await self.db_service.get_user_by_username(payload.get("sub"))
            except NoResultFound:
                return None

            if not await self.verify_invitation_code(invitation_code) and not user.is_active:
                raise ForbiddenError("User is not active, may be active first or use another user")

            if payload.get("type") == "refresh":
                jti = payload.get("jti")
                if not jti:
                    return None

                try:
                    token_info = await self.db_service.get_revoked_token(jti)
                    if token_info.revoked_by:  # Si le token a déjà été utilisé
                        return None
                except Exception:
                    return None

            return payload
        except PyJWTError as error:
            logger.error(error)
            return None

    async def refresh_access_token(self, payload: dict, audience: str, device_info: Optional[dict] = None) -> dict:
        try:
            if payload.get("type") != "refresh":
                raise PyJWTError("Invalid token type")

            jti = payload.get("jti")
            if not jti:
                raise PyJWTError("Invalid token: no JTI")

            revoked_token = await self.db_service.get_revoked_token(jti)
            if not revoked_token:
                raise PyJWTError("Token not found in database")
            if revoked_token.revoked_by:
                raise PyJWTError("Token has been revoked")

            user_data = {
                "sub": payload.get("sub"),
                "is_superuser": payload.get("is_superuser", False)
            }

            if device_info:
                user_data["device_info"] = device_info

            new_access_token, payload_access_token = await self.create_access_token(user_data, audience=audience)
            new_refresh_token, _ = await self.create_refresh_token(user_data, audience=audience)

            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "expires_at": payload_access_token.get("exp")
            }
        except PyJWTError as e:
            raise UnauthorizedError(
                message=f"Could not validate credentials: {str(e)}"
            )

    async def authenticate_user(self, username_or_handle: str, password: str):
        try:
            user = await self.db_service.get_user_by_username(username_or_handle)
        except NoResultFound:
            try:
                user = await self.db_service.get_user_by_handle(username_or_handle)
            except NoResultFound:
                user = None
        if not user:
            user = await self.db_service.get_user_by_handle(username_or_handle)

        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def revoke_token(self, jti: Optional[str]):
        if jti:
            await self.db_service.delete_revoked_token(jti)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)