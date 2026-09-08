from fastapi import APIRouter

from app.core.security import create_access_token
from app.schemas.auth import Token

router = APIRouter(prefix="/auth", tags=["Auth"])


# Login Api for admin
@router.post("/login", response_model=Token)
async def login():
    return {
        "access_token": create_access_token({"username": "admin"}),
        "token_type": "bearer",
    }
