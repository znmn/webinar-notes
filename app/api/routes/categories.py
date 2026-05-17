from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.core.logger import get_logger
from app.db.session import get_db
from app.models.category import Category
from app.schemas.category import CategoriesListResponse, CategoryResponse

router = APIRouter(tags=["categories"])
logger = get_logger(__name__)


@router.get("/categories", response_model=CategoriesListResponse)
def get_categories(
    search: str | None = Query(default=None, min_length=1, max_length=50),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CategoriesListResponse:
    """Return all supported categories."""
    _ = current_user
    try:
        query = db.query(Category)
        if search is not None:
            search_term = f"%{search.strip()}%"
            query = query.filter(Category.name.ilike(search_term))
        total = query.count()
        categories = (
            query.order_by(Category.name.asc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
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
        count=len(response_data),
        total=total,
        page=page,
        size=size,
        categories=response_data,
    )
