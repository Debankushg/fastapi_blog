from sqlalchemy.orm import Session

from app.models.user_model import User
from app.repositories import role_repository, user_repository
from app.utils.constants import DEFAULT_ROLE
from app.utils.exceptions import ConflictError, NotFoundError
from app.utils.security import hash_password
from app.validators.user_validator import UserCreate


def create_user(db: Session, data: UserCreate) -> User:
    if user_repository.find_by_username(db, data.username):
        raise ConflictError("Username already registered")
    if user_repository.find_by_email(db, data.email):
        raise ConflictError("Email already registered")
    default_role = role_repository.find_by_name(db, DEFAULT_ROLE)
    return user_repository.create(
        db,
        data.username,
        data.email,
        hash_password(data.password),
        roles=[default_role] if default_role else [],
    )


def list_users(db: Session, page: int, limit: int, search: str):
    return user_repository.find_all(db, page, limit, search)


def get_user(db: Session, user_id: int) -> User:
    user = user_repository.find_by_id(db, user_id)
    if not user:
        raise NotFoundError(f"User with id {user_id} not found")
    return user


def update_user(db: Session, user_id: int, data: UserCreate) -> User:
    user = get_user(db, user_id)
    return user_repository.update(
        db, user, data.username, data.email, hash_password(data.password)
    )


def delete_user(db: Session, user_id: int) -> None:
    user = get_user(db, user_id)
    user_repository.delete(db, user)
