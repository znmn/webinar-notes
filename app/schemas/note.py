from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, StringConstraints

TitleStr = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
]
DescriptionStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=4000),
]
CategoryNameStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, to_lower=True, min_length=1, max_length=50
    ),
]


class NoteCreateBody(BaseModel):
    title: TitleStr
    description: Optional[DescriptionStr] = None
    category: CategoryNameStr


class NoteUpdateBody(BaseModel):
    title: Optional[TitleStr] = None
    description: Optional[DescriptionStr] = None
    category: Optional[CategoryNameStr] = None


class NoteResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    category: str
    created_at: datetime | None
    updated_at: datetime | None


class NotesListResponse(BaseModel):
    count: int
    total: int
    page: int
    size: int
    notes: list[NoteResponse]


class NoteMutationResponse(BaseModel):
    message: str
    note: NoteResponse


class NoteDeleteResponse(BaseModel):
    message: str
    deleted_id: int
