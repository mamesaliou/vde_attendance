from functools import wraps
from sqlalchemy.exc import NoResultFound

from app.core.exceptions import (
    ApiError,
    ForbiddenError, NotFoundError
)


def handle_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except NoResultFound:
            raise NotFoundError(f"resource_name not found for [{args}, {kwargs}]")
        except ApiError:
            raise
        except Exception as e:
            raise ApiError(
                message="Une erreur interne s'est produite",
                details=str(e),
                status_code=500
            )
    return wrapper

def require_superuser():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs['request']
            if not request.state.token_data.get("is_superuser"):
                raise ForbiddenError("Cette action nécessite des droits super utilisateur")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
