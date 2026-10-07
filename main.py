from fastapi import FastAPI

from app import models  # noqa: F401  (registers tables with Base)
from app.config.database import Base, engine
from app.config.settings import settings
from app.middleware.error_middleware import register_error_handlers
from app.routes import api_router
from app.utils.seed import seed_defaults

Base.metadata.create_all(bind=engine)
seed_defaults()

app = FastAPI(title=settings.APP_NAME)

register_error_handlers(app)
app.include_router(api_router)


# Home route
@app.get("/")
async def home():
    return {"message": "Hello World blog api started"}
