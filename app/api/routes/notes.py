from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.core.config import ALLOWED_CATEGORY
from app.core.logger import get_logger
from app.core.utils.datetime import utc_now
from app.db.session import get_db
from app.models.note import Note
from app.schemas.note import (
    NoteCreateBody,
    NoteDeleteResponse,
    NoteMutationResponse,
    NoteResponse,
    NotesListResponse,
    NoteUpdateBody,
)

router = APIRouter()
logger = get_logger(__name__)


@router.get("/notes", response_model=NotesListResponse)
def get_notes(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotesListResponse:
    """Return all notes that belong to the authenticated user."""
    try:
        user_notes = (
            db.query(Note).filter(Note.user_id == current_user.id).all()
        )
    except SQLAlchemyError as exc:
        logger.exception("Database error while listing notes")
        raise HTTPException(
            status_code=500, detail="internal server error"
        ) from exc
    note_list = [
        NoteResponse.model_validate(note, from_attributes=True)
        for note in user_notes
    ]
    return NotesListResponse(count=len(note_list), notes=note_list)


@router.get("/notes/{note_id}", response_model=NoteResponse)
def get_note_detail(
    note_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NoteResponse:
    """Return detail for one note owned by the authenticated user."""
    try:
        note = (
            db.query(Note)
            .filter(Note.id == note_id, Note.user_id == current_user.id)
            .first()
        )
    except SQLAlchemyError as exc:
        logger.exception("Database error while fetching note detail")
        raise HTTPException(
            status_code=500, detail="internal server error"
        ) from exc
    if not note:
        logger.info(
            "Note detail not found: note_id=%s user_id=%s",
            note_id,
            current_user.id,
        )
        raise HTTPException(status_code=404, detail="note not found")
    return NoteResponse.model_validate(note, from_attributes=True)


@router.post("/notes", response_model=NoteMutationResponse)
def create_note(
    note_payload: NoteCreateBody,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NoteMutationResponse:
    """Create a new note for the authenticated user."""
    if note_payload.category not in ALLOWED_CATEGORY:
        logger.info("Rejected create note due to invalid category")
        raise HTTPException(status_code=400, detail="invalid category")
    if len(note_payload.title.strip()) == 0:
        logger.info("Rejected create note due to empty title")
        raise HTTPException(status_code=400, detail="title cannot be empty")

    note = Note(
        user_id=current_user.id,
        title=note_payload.title,
        description=note_payload.description,
        category=note_payload.category,
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    try:
        db.add(note)
        db.commit()
        db.refresh(note)
        logger.info(
            "Note created: note_id=%s user_id=%s", note.id, current_user.id
        )
        return NoteMutationResponse(
            message="note created",
            note=NoteResponse.model_validate(note, from_attributes=True),
        )
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Database error while creating note")
        raise HTTPException(
            status_code=500, detail="internal server error"
        ) from exc


@router.put("/notes/{note_id}", response_model=NoteMutationResponse)
def update_note(
    note_id: int,
    note_update_payload: NoteUpdateBody,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NoteMutationResponse:
    """Update an existing note owned by the authenticated user."""
    try:
        note = (
            db.query(Note)
            .filter(Note.id == note_id, Note.user_id == current_user.id)
            .first()
        )
    except SQLAlchemyError as exc:
        logger.exception("Database error while fetching note for update")
        raise HTTPException(
            status_code=500, detail="internal server error"
        ) from exc
    if not note:
        logger.info(
            "Update note not found: note_id=%s user_id=%s",
            note_id,
            current_user.id,
        )
        raise HTTPException(status_code=404, detail="note not found")

    if note_update_payload.category is not None:
        if note_update_payload.category not in ALLOWED_CATEGORY:
            logger.info("Rejected update note due to invalid category")
            raise HTTPException(status_code=400, detail="invalid category")
        setattr(note, "category", note_update_payload.category)

    if note_update_payload.title is not None:
        if len(note_update_payload.title.strip()) == 0:
            logger.info("Rejected update note due to empty title")
            raise HTTPException(
                status_code=400,
                detail="title cannot be empty",
            )
        setattr(note, "title", note_update_payload.title)

    if note_update_payload.description is not None:
        setattr(note, "description", note_update_payload.description)

    setattr(note, "updated_at", utc_now())
    try:
        db.commit()
        db.refresh(note)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Database error while updating note")
        raise HTTPException(
            status_code=500, detail="internal server error"
        ) from exc

    logger.info(
        "Note updated: note_id=%s user_id=%s", note.id, current_user.id
    )
    return NoteMutationResponse(
        message="note updated",
        note=NoteResponse.model_validate(note, from_attributes=True),
    )


@router.delete("/notes/{note_id}", response_model=NoteDeleteResponse)
def remove_note(
    note_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NoteDeleteResponse:
    """Delete a note owned by the authenticated user."""
    try:
        note = (
            db.query(Note)
            .filter(Note.id == note_id, Note.user_id == current_user.id)
            .first()
        )
    except SQLAlchemyError as exc:
        logger.exception("Database error while fetching note for delete")
        raise HTTPException(
            status_code=500, detail="internal server error"
        ) from exc
    if not note:
        logger.info(
            "Delete note not found: note_id=%s user_id=%s",
            note_id,
            current_user.id,
        )
        raise HTTPException(status_code=404, detail="note not found")

    try:
        db.delete(note)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Database error while deleting note")
        raise HTTPException(
            status_code=500, detail="internal server error"
        ) from exc

    logger.info(
        "Note deleted: note_id=%s user_id=%s", note_id, current_user.id
    )
    return NoteDeleteResponse(message="note deleted", deleted_id=note_id)
