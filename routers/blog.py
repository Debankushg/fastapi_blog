from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import verify_access_token
from app.crud import blog as blog_crud
from app.db.session import get_db
from app.schemas.blog import BlogCreate, BlogCreateResponse, BlogListResponse, BlogResponse

router = APIRouter(tags=["Blogs"])


# Create Blog (Admin Only)
@router.post("/blog", status_code=201, response_model=BlogCreateResponse)
async def create_blog(
    blog: BlogCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_access_token),
):
    new_blog = blog_crud.create_blog(db, blog)
    return {"message": "Blog created successfully", "blog": new_blog}


# Read All Blogs
@router.get("/blogs", response_model=BlogListResponse)
async def get_blogs(
    page: int = 1,
    limit: int = 10,
    search: str = Query(default=""),
    db: Session = Depends(get_db),
):
    blogs, total = blog_crud.get_blogs(db, page, limit, search)
    return {
        "message": "Blogs fetched successfully",
        "page": page,
        "limit": limit,
        "blogs": blogs,
        "total": total,
    }


# Read Single Blog
@router.get("/blog/{id}", response_model=BlogResponse)
async def get_blog(id: int, db: Session = Depends(get_db)):
    blog = blog_crud.get_blog(db, id)
    if not blog:
        raise HTTPException(status_code=404, detail=f"Blog with id {id} not found")
    return blog


# Update Blog Api (Admin Only)
@router.put("/blog/{id}", response_model=BlogCreateResponse)
async def update_blog(
    id: int,
    blog: BlogCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_access_token),
):
    updated_blog = blog_crud.update_blog(db, id, blog)
    if not updated_blog:
        raise HTTPException(status_code=404, detail=f"Blog with id {id} not found")
    return {"message": "Blog updated successfully", "blog": updated_blog}


# Delete Blog Api (Admin Only)
@router.delete("/blog/{id}", status_code=200)
async def delete_blog(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_access_token),
):
    deleted = blog_crud.delete_blog(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Blog with id {id} not found")
    return {"message": "Blog deleted successfully"}


# Delete All Blogs Api (Admin Only)
@router.delete("/blogs", status_code=200)
async def delete_all_blogs(
    db: Session = Depends(get_db),
    user=Depends(verify_access_token),
):
    blog_crud.delete_all_blogs(db)
    return {"message": "All Blogs deleted successfully"}
