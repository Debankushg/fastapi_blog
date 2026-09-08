from sqlalchemy.orm import Session

from app.models.blog import Blog
from app.schemas.blog import BlogCreate


def create_blog(db: Session, blog: BlogCreate) -> Blog:
    new_blog = Blog(title=blog.title, content=blog.content)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


def get_blogs(db: Session, page: int, limit: int, search: str):
    query = db.query(Blog)
    if search:
        query = query.filter(Blog.title.ilike(f"%{search}%"))

    total = query.count()
    blogs = query.offset((page - 1) * limit).limit(limit).all()
    return blogs, total


def get_blog(db: Session, blog_id: int) -> Blog | None:
    return db.query(Blog).filter(Blog.id == blog_id).first()


def update_blog(db: Session, blog_id: int, blog: BlogCreate) -> Blog | None:
    blog_to_update = get_blog(db, blog_id)
    if not blog_to_update:
        return None
    blog_to_update.title = blog.title
    blog_to_update.content = blog.content
    db.commit()
    db.refresh(blog_to_update)
    return blog_to_update


def delete_blog(db: Session, blog_id: int) -> bool:
    blog_to_delete = get_blog(db, blog_id)
    if not blog_to_delete:
        return False
    db.delete(blog_to_delete)
    db.commit()
    return True


def delete_all_blogs(db: Session) -> None:
    db.query(Blog).delete()
    db.commit()
