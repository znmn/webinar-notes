from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.core.config import ALLOWED_CATEGORY
from app.core.utils.datetime import utc_now
from app.db.session import get_db
from app.models.note import Note
from app.schemas.note import NoteCreateBody, NoteUpdateBody

router = APIRouter()


@router.get("/notes")
def get_notes(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_notes = db.query(Note).filter(Note.user_id == current_user.id).all()
    note_list = []
    for note in user_notes:
        note_list.append(
            {
                "id": note.id,
                "user_id": note.user_id,
                "title": note.title,
                "description": note.description,
                "category": note.category,
                "created_at": note.created_at,
                "updated_at": note.updated_at,
            }
        )
    return {"count": len(note_list), "notes": note_list}


@router.get("/notes/{note_id}")
def get_note_detail(
    note_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == current_user.id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="note not found")
    return {
        "id": note.id,
        "user_id": note.user_id,
        "title": note.title,
        "description": note.description,
        "category": note.category,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
    }


@router.post("/notes")
def create_note(
    note_payload: NoteCreateBody,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if note_payload.category not in ALLOWED_CATEGORY:
        raise HTTPException(status_code=400, detail="invalid category")
    if len(note_payload.title.strip()) == 0:
        raise HTTPException(status_code=400, detail="title cannot be empty")

    note = Note(
        user_id=current_user.id,
        title=note_payload.title,
        description=note_payload.description,
        category=note_payload.category,
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return {
        "message": "note created",
        "note": {
            "id": note.id,
            "user_id": note.user_id,
            "title": note.title,
            "description": note.description,
            "category": note.category,
            "created_at": note.created_at,
            "updated_at": note.updated_at,
        },
    }


@router.put("/notes/{note_id}")
def update_note(
    note_id: int,
    note_update_payload: NoteUpdateBody,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == current_user.id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="note not found")

    if note_update_payload.category is not None:
        if note_update_payload.category not in ALLOWED_CATEGORY:
            raise HTTPException(status_code=400, detail="invalid category")
        setattr(note, "category", note_update_payload.category)

    if note_update_payload.title is not None:
        if len(note_update_payload.title.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="title cannot be empty",
            )
        setattr(note, "title", note_update_payload.title)

    if note_update_payload.description is not None:
        setattr(note, "description", note_update_payload.description)

    setattr(note, "updated_at", utc_now())
    db.commit()
    db.refresh(note)

    return {
        "message": "note updated",
        "note": {
            "id": note.id,
            "user_id": note.user_id,
            "title": note.title,
            "description": note.description,
            "category": note.category,
            "updated_at": note.updated_at,
        },
    }


@router.delete("/notes/{note_id}")
def remove_note(
    note_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == current_user.id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="note not found")

    db.delete(note)
    db.commit()

    return {"message": "note deleted", "deleted_id": note_id}
