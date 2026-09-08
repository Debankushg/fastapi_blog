from pydantic import BaseModel


# Input schema
class BlogCreate(BaseModel):
    title: str
    content: str


# Output schema
class BlogResponse(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True


# Wrapped response with a message
class BlogCreateResponse(BaseModel):
    message: str
    blog: BlogResponse


# Paginated list response
class BlogListResponse(BaseModel):
    message: str
    page: int
    limit: int
    blogs: list[BlogResponse]
    total: int
