from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.notes import router as notes_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(notes_router)
