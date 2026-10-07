from sqlalchemy.orm import Session

from app.models.blog_model import Blog
from app.repositories import blog_repository
from app.utils.exceptions import NotFoundError
from app.validators.blog_validator import BlogCreate


def create_blog(db: Session, data: BlogCreate) -> Blog:
    return blog_repository.create(db, data.title, data.content)


def list_blogs(db: Session, page: int, limit: int, search: str):
    return blog_repository.find_all(db, page, limit, search)


def get_blog(db: Session, blog_id: int) -> Blog:
    blog = blog_repository.find_by_id(db, blog_id)
    if not blog:
        raise NotFoundError(f"Blog with id {blog_id} not found")
    return blog


def update_blog(db: Session, blog_id: int, data: BlogCreate) -> Blog:
    blog = get_blog(db, blog_id)
    return blog_repository.update(db, blog, data.title, data.content)


def delete_blog(db: Session, blog_id: int) -> None:
    blog = get_blog(db, blog_id)
    blog_repository.delete(db, blog)


def delete_all_blogs(db: Session) -> None:
    blog_repository.delete_all(db)
