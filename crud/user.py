from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


def create_user(db: Session, user: UserCreate) -> User:
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_users(db: Session, page: int, limit: int, search: str):
    query = db.query(User)
    if search:
        query = query.filter(User.username.ilike(f"%{search}%"))

    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()
    return users, total


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def update_user(db: Session, user_id: int, user: UserCreate) -> User | None:
    user_to_update = get_user(db, user_id)
    if not user_to_update:
        return None
    user_to_update.username = user.username
    user_to_update.email = user.email
    user_to_update.hashed_password = hash_password(user.password)
    db.commit()
    db.refresh(user_to_update)
    return user_to_update


def delete_user(db: Session, user_id: int) -> bool:
    user_to_delete = get_user(db, user_id)
    if not user_to_delete:
        return False
    db.delete(user_to_delete)
    db.commit()
    return True
