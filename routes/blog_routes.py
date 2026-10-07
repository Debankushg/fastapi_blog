from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers import blog_controller
from app.middleware.auth_middleware import require_permission
from app.validators.blog_validator import (
    BlogCreate,
    BlogCreateResponse,
    BlogListResponse,
    BlogResponse,
)

router = APIRouter(tags=["Blogs"])


# Create Blog
@router.post("/blog", status_code=201, response_model=BlogCreateResponse)
async def create_blog(
    blog: BlogCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("blog", "create")),
):
    return await blog_controller.create_blog(db, blog)


# Read All Blogs
@router.get("/blogs", response_model=BlogListResponse)
async def get_blogs(
    page: int = 1,
    limit: int = 10,
    search: str = Query(default=""),
    db: Session = Depends(get_db),
    _=Depends(require_permission("blog", "read")),
):
    return await blog_controller.get_blogs(db, page, limit, search)


# Read Single Blog
@router.get("/blog/{id}", response_model=BlogResponse)
async def get_blog(
    id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("blog", "read")),
):
    return await blog_controller.get_blog(db, id)


# Update Blog
@router.put("/blog/{id}", response_model=BlogCreateResponse)
async def update_blog(
    id: int,
    blog: BlogCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("blog", "write")),
):
    return await blog_controller.update_blog(db, id, blog)


# Delete Blog
@router.delete("/blog/{id}", status_code=200)
async def delete_blog(
    id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("blog", "delete")),
):
    return await blog_controller.delete_blog(db, id)


# Delete All Blogs
@router.delete("/blogs", status_code=200)
async def delete_all_blogs(
    db: Session = Depends(get_db),
    _=Depends(require_permission("blog", "delete")),
):
    return await blog_controller.delete_all_blogs(db)
