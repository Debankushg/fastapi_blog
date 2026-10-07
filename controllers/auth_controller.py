from sqlalchemy.orm import Session

from app.services import auth_service, user_service
from app.utils.permissions import effective_permissions, is_admin
from app.validators.user_validator import UserCreate


async def register(db: Session, data: UserCreate):
    user = user_service.create_user(db, data)
    return {"message": "User registered successfully", "user": user}


async def login(db: Session, identifier: str, password: str):
    return auth_service.login(db, identifier, password)


async def me(user):
    return {
        "user": user,
        "is_admin": is_admin(user),
        "permissions": effective_permissions(user),
    }
