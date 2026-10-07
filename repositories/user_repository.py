from sqlalchemy.orm import Session

from app.models.role_model import Role
from app.models.user_model import User


def create(
    db: Session,
    username: str,
    email: str,
    hashed_password: str,
    roles: list[Role] | None = None,
) -> User:
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        roles=roles or [],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def find_all(db: Session, page: int, limit: int, search: str):
    query = db.query(User)
    if search:
        query = query.filter(User.username.ilike(f"%{search}%"))

    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()
    return users, total


def find_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def find_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def find_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def find_by_username_or_email(db: Session, identifier: str) -> User | None:
    return (
        db.query(User)
        .filter((User.username == identifier) | (User.email == identifier.lower()))
        .first()
    )


def update(
    db: Session, user: User, username: str, email: str, hashed_password: str
) -> User:
    user.username = username
    user.email = email
    user.hashed_password = hashed_password
    db.commit()
    db.refresh(user)
    return user


def delete(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


def set_roles(db: Session, user: User, roles: list[Role]) -> User:
    user.roles = roles
    db.commit()
    db.refresh(user)
    return user
