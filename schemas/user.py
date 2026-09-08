from pydantic import BaseModel, EmailStr


# Input schema
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


# Output schema (never expose hashed_password)
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


# Wrapped response with a message
class UserCreateResponse(BaseModel):
    message: str
    user: UserResponse


# Paginated list response
class UserListResponse(BaseModel):
    message: str
    page: int
    limit: int
    users: list[UserResponse]
    total: int
