from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: int
    name: str


class CategoriesListResponse(BaseModel):
    count: int
    total: int
    page: int
    size: int
    categories: list[CategoryResponse]
