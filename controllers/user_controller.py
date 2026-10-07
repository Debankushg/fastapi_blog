from sqlalchemy.orm import Session

from app.services import user_service
from app.validators.user_validator import UserCreate


async def get_users(db: Session, page: int, limit: int, search: str):
    users, total = user_service.list_users(db, page, limit, search)
    return {
        "message": "Users fetched successfully",
        "page": page,
        "limit": limit,
        "users": users,
        "total": total,
    }


async def get_user(db: Session, user_id: int):
    return user_service.get_user(db, user_id)


async def update_user(db: Session, user_id: int, data: UserCreate):
    user = user_service.update_user(db, user_id, data)
    return {"message": "User updated successfully", "user": user}


async def delete_user(db: Session, user_id: int):
    user_service.delete_user(db, user_id)
    return {"message": "User deleted successfully"}
