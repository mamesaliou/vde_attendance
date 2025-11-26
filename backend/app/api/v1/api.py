"""
Main API router that includes all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.routers import auth, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

