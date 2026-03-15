from fastapi import APIRouter

from app.api.routes import admin, auth, dashboard, practice, quiz

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(practice.router, prefix="/problems", tags=["practice"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
