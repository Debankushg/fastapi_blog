from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import verify_access_token
from app.crud import user as user_crud
from app.db.session import get_db
from app.schemas.user import UserCreate, UserCreateResponse, UserListResponse, UserResponse

router = APIRouter(tags=["Users"])


# Create User
@router.post("/user", status_code=201, response_model=UserCreateResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if user_crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=409, detail="Username already registered")
    new_user = user_crud.create_user(db, user)
    return {"message": "User created successfully", "user": new_user}


# Read All Users
@router.get("/users", response_model=UserListResponse)
async def get_users(
    page: int = 1,
    limit: int = 10,
    search: str = Query(default=""),
    db: Session = Depends(get_db),
):
    users, total = user_crud.get_users(db, page, limit, search)
    return {
        "message": "Users fetched successfully",
        "page": page,
        "limit": limit,
        "users": users,
        "total": total,
    }


# Read Single User
@router.get("/user/{id}", response_model=UserResponse)
async def get_user(id: int, db: Session = Depends(get_db)):
    user = user_crud.get_user(db, id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found")
    return user


# Update User (Admin Only)
@router.put("/user/{id}", response_model=UserCreateResponse)
async def update_user(
    id: int,
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(verify_access_token),
):
    updated_user = user_crud.update_user(db, id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found")
    return {"message": "User updated successfully", "user": updated_user}


# Delete User (Admin Only)
@router.delete("/user/{id}", status_code=200)
async def delete_user(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(verify_access_token),
):
    deleted = user_crud.delete_user(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found")
    return {"message": "User deleted successfully"}
