from typing import Optional

from pydantic import BaseModel


class NoteCreateBody(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = None
    category: str


class NoteUpdateBody(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
