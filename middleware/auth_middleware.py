from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.user_model import User
from app.repositories import user_repository
from app.utils.permissions import has_permission, is_admin
from app.utils.security import decode_access_token

bearer_scheme = HTTPBearer()


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def verify_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    try:
        return decode_access_token(credentials.credentials)
    except JWTError:
        raise _unauthorized()


def get_current_user(
    payload: dict = Depends(verify_access_token), db: Session = Depends(get_db)
) -> User:
    """Load the logged-in user (with roles) from the token's `sub` claim."""
    subject = str(payload.get("sub", ""))
    user = user_repository.find_by_id(db, int(subject)) if subject.isdigit() else None
    if not user:
        raise _unauthorized()
    return user


def require_permission(resource: str, action: str):
    """Dependency factory: allow only users whose roles grant `action` on `resource`."""

    def checker(user: User = Depends(get_current_user)) -> User:
        if not has_permission(user, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have '{action}' permission on '{resource}'",
            )
        return user

    return checker


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not is_admin(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return user
