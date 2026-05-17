from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.core.logger import get_logger
from app.db.session import get_db
from app.models.category import Category
from app.schemas.category import CategoriesListResponse, CategoryResponse

router = APIRouter()
logger = get_logger(__name__)


@router.get("/categories", response_model=CategoriesListResponse)
def get_categories(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CategoriesListResponse:
    """Return all supported categories."""
    _ = current_user
    try:
        categories = db.query(Category).order_by(Category.name.asc()).all()
    except SQLAlchemyError as exc:
        logger.exception("Database error while listing categories")
        raise HTTPException(
            status_code=500, detail="internal server error"
        ) from exc
    response_data = [
        CategoryResponse.model_validate(category, from_attributes=True)
        for category in categories
    ]
    return CategoriesListResponse(
        count=len(response_data), categories=response_data
    )
