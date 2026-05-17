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
    all_notes = db.query(Note).filter(Note.user_id == current_user.id).all()
    result = []
    for note in all_notes:
        result.append(
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
    return {"count": len(result), "notes": result}


@router.get("/notes/{id}")
def get_note_detail(
    id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = (
        db.query(Note)
        .filter(Note.id == id, Note.user_id == current_user.id)
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
    data: NoteCreateBody,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.category not in ALLOWED_CATEGORY:
        raise HTTPException(status_code=400, detail="invalid category")
    if len(data.title.strip()) == 0:
        raise HTTPException(status_code=400, detail="title cannot be empty")

    note = Note(
        user_id=current_user.id,
        title=data.title,
        description=data.description,
        category=data.category,
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


@router.put("/notes/{id}")
def update_note(
    id: int,
    data: NoteUpdateBody,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = (
        db.query(Note)
        .filter(Note.id == id, Note.user_id == current_user.id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="note not found")

    if data.category is not None:
        if data.category not in ALLOWED_CATEGORY:
            raise HTTPException(status_code=400, detail="invalid category")
        setattr(note, "category", data.category)

    if data.title is not None:
        if len(data.title.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="title cannot be empty",
            )
        setattr(note, "title", data.title)

    if data.description is not None:
        setattr(note, "description", data.description)

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


@router.delete("/notes/{id}")
def remove_note(
    id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = (
        db.query(Note)
        .filter(Note.id == id, Note.user_id == current_user.id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="note not found")

    db.delete(note)
    db.commit()

    return {"message": "note deleted", "deleted_id": id}
