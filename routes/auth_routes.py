from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers import auth_controller
from app.middleware.auth_middleware import get_current_user
from app.validators.auth_validator import LoginRequest, MeResponse, TokenResponse
from app.validators.user_validator import UserCreate, UserCreateResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


# Register a new user
@router.post("/register", status_code=201, response_model=UserCreateResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    return await auth_controller.register(db, user)


# Login with email and password
@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    return await auth_controller.login(db, credentials.email, credentials.password)


# Current user with roles and effective permissions
@router.get("/me", response_model=MeResponse)
async def me(user=Depends(get_current_user)):
    return await auth_controller.me(user)
