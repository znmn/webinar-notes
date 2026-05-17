from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NoteCreateBody(BaseModel):
    title: str
    description: Optional[str] = None
    category: str


class NoteUpdateBody(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


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
    notes: list[NoteResponse]


class NoteMutationResponse(BaseModel):
    message: str
    note: NoteResponse


class NoteDeleteResponse(BaseModel):
    message: str
    deleted_id: int
