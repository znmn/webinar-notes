from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: int
    name: str


class CategoriesListResponse(BaseModel):
    count: int
    categories: list[CategoryResponse]
