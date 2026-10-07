from sqlalchemy.orm import Session

from app.models.blog_model import Blog


def create(db: Session, title: str, content: str) -> Blog:
    blog = Blog(title=title, content=content)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


def find_all(db: Session, page: int, limit: int, search: str):
    query = db.query(Blog)
    if search:
        query = query.filter(Blog.title.ilike(f"%{search}%"))

    total = query.count()
    blogs = query.offset((page - 1) * limit).limit(limit).all()
    return blogs, total


def find_by_id(db: Session, blog_id: int) -> Blog | None:
    return db.query(Blog).filter(Blog.id == blog_id).first()


def update(db: Session, blog: Blog, title: str, content: str) -> Blog:
    blog.title = title
    blog.content = content
    db.commit()
    db.refresh(blog)
    return blog


def delete(db: Session, blog: Blog) -> None:
    db.delete(blog)
    db.commit()


def delete_all(db: Session) -> None:
    db.query(Blog).delete()
    db.commit()
