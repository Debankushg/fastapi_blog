from sqlalchemy.orm import Session

from app.config.settings import settings
from app.repositories import user_repository
from app.utils.exceptions import UnauthorizedError
from app.utils.security import create_access_token, verify_password


def login(db: Session, identifier: str, password: str) -> dict:
    """Authenticate with username or email and return a bearer token."""
    user = user_repository.find_by_username_or_email(db, identifier.strip())
    # Same error for unknown user and wrong password to avoid user enumeration
    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Incorrect username/email or password")

    token = create_access_token({"sub": str(user.id), "username": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
