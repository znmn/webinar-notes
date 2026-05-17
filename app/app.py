from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import APP_ENV
from app.core.logger import setup_logging

setup_logging()
is_prod = APP_ENV == "prod"
app = FastAPI(
    title="notes-backend",
    docs_url=None if is_prod else "/docs",
    redoc_url=None if is_prod else "/redoc",
    openapi_url=None if is_prod else "/openapi.json",
)
app.include_router(api_router)
