from fastapi import APIRouter

from app.routes import auth_routes, blog_routes, role_routes, user_routes

api_router = APIRouter()
api_router.include_router(auth_routes.router)
api_router.include_router(blog_routes.router)
api_router.include_router(user_routes.router)
api_router.include_router(role_routes.router)
