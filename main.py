from fastapi import FastAPI

from app.db.session import Base, engine
from app.models import blog as blog_model  # noqa: F401  (registers table with Base)
from app.models import user as user_model  # noqa: F401  (registers table with Base)
from app.routers import auth, blog, user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Python Blog API")

app.include_router(auth.router)
app.include_router(blog.router)
app.include_router(user.router)


# Home route
@app.get("/")
async def home():
    return {"message": "Hello World blog api started"}
