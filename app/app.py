from fastapi import FastAPI

from app.api.router import api_router
from app.core.logger import setup_logging

setup_logging()
app = FastAPI(title="notes-backend")
app.include_router(api_router)
