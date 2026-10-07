from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers import user_controller
from app.middleware.auth_middleware import require_permission
from app.validators.user_validator import (
    UserCreate,
    UserCreateResponse,
    UserListResponse,
    UserResponse,
)

router = APIRouter(tags=["Users"])


# Read All Users
@router.get("/users", response_model=UserListResponse)
async def get_users(
    page: int = 1,
    limit: int = 10,
    search: str = Query(default=""),
    db: Session = Depends(get_db),
    _=Depends(require_permission("user", "read")),
):
    return await user_controller.get_users(db, page, limit, search)


# Read Single User
@router.get("/user/{id}", response_model=UserResponse)
async def get_user(
    id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("user", "read")),
):
    return await user_controller.get_user(db, id)


# Update User
@router.put("/user/{id}", response_model=UserCreateResponse)
async def update_user(
    id: int,
    user: UserCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("user", "write")),
):
    return await user_controller.update_user(db, id, user)


# Delete User
@router.delete("/user/{id}", status_code=200)
async def delete_user(
    id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("user", "delete")),
):
    return await user_controller.delete_user(db, id)
