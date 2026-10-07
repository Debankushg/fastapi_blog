from sqlalchemy.orm import Session

from app.services import blog_service
from app.validators.blog_validator import BlogCreate


async def create_blog(db: Session, data: BlogCreate):
    blog = blog_service.create_blog(db, data)
    return {"message": "Blog created successfully", "blog": blog}


async def get_blogs(db: Session, page: int, limit: int, search: str):
    blogs, total = blog_service.list_blogs(db, page, limit, search)
    return {
        "message": "Blogs fetched successfully",
        "page": page,
        "limit": limit,
        "blogs": blogs,
        "total": total,
    }


async def get_blog(db: Session, blog_id: int):
    return blog_service.get_blog(db, blog_id)


async def update_blog(db: Session, blog_id: int, data: BlogCreate):
    blog = blog_service.update_blog(db, blog_id, data)
    return {"message": "Blog updated successfully", "blog": blog}


async def delete_blog(db: Session, blog_id: int):
    blog_service.delete_blog(db, blog_id)
    return {"message": "Blog deleted successfully"}


async def delete_all_blogs(db: Session):
    blog_service.delete_all_blogs(db)
    return {"message": "All Blogs deleted successfully"}
