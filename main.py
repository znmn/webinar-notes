import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker


def _load_env_file() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _get_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise ValueError(f"Environment variable '{name}' is required")
    return value


_load_env_file()

DATABASE_URL = _get_env("DATABASE_URL")
SECRET = _get_env("SECRET")
ALGORITHM = _get_env("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(_get_env("ACCESS_TOKEN_EXPIRE_MINUTES"))

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(title="notes-backend")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class RegisterBody(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginBody(BaseModel):
    email: EmailStr
    password: str


class NoteCreateBody(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = None
    category: str


class NoteUpdateBody(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


ALLOWED_CATEGORY = ["work", "personal", "finance", "learning", "other"]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def make_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    t = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return t


def get_current_user(
    authorization: str = Header(default=None), db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(
            status_code=401, detail="missing authorization header"
        )
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="invalid authorization format"
        )

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        uid = payload.get("user_id")
        if uid is None:
            raise HTTPException(status_code=401, detail="bad token")
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")

    u = db.query(User).filter(User.id == uid).first()
    if not u:
        raise HTTPException(status_code=401, detail="user not found")
    return u


@app.post("/register")
def register(body: RegisterBody, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="email already used")

    user = User(name=body.name, email=body.email, password=body.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "message": "register success",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at,
        },
    }


@app.post("/login")
def login(payload: LoginBody, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="email/password salah")

    if payload.password != user.password:
        raise HTTPException(status_code=401, detail="email/password salah")

    token = make_token({"user_id": user.id, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "name": user.name, "email": user.email},
    }


@app.get("/notes")
def get_notes(
    current=Depends(get_current_user), db: Session = Depends(get_db)
):
    all_notes = db.query(Note).all()
    result = []
    for n in all_notes:
        result.append(
            {
                "id": n.id,
                "user_id": n.user_id,
                "title": n.title,
                "description": n.description,
                "category": n.category,
                "created_at": n.created_at,
                "updated_at": n.updated_at,
            }
        )
    return {"count": len(result), "notes": result}


@app.get("/notes/{id}")
def get_note_detail(
    id: int, current=Depends(get_current_user), db: Session = Depends(get_db)
):
    note = db.query(Note).filter(Note.id == id).first()
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


@app.post("/notes")
def create_note(
    data: NoteCreateBody,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.category not in ALLOWED_CATEGORY:
        raise HTTPException(status_code=400, detail="invalid category")
    if len(data.title.strip()) == 0:
        raise HTTPException(status_code=400, detail="title cannot be empty")

    n = Note(
        user_id=data.user_id,
        title=data.title,
        description=data.description,
        category=data.category,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(n)
    db.commit()
    db.refresh(n)
    return {
        "message": "note created",
        "note": {
            "id": n.id,
            "user_id": n.user_id,
            "title": n.title,
            "description": n.description,
            "category": n.category,
            "created_at": n.created_at,
            "updated_at": n.updated_at,
        },
    }


@app.put("/notes/{id}")
def update_note(
    id: int,
    data: NoteUpdateBody,
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = db.query(Note).filter(Note.id == id).first()
    if not note:
        raise HTTPException(status_code=404, detail="note not found")

    if data.category is not None:
        if data.category not in ALLOWED_CATEGORY:
            raise HTTPException(status_code=400, detail="invalid category")
        setattr(note, "category", data.category)

    if data.title is not None:
        if len(data.title.strip()) == 0:
            raise HTTPException(
                status_code=400, detail="title cannot be empty"
            )
        setattr(note, "title", data.title)

    if data.description is not None:
        setattr(note, "description", data.description)

    setattr(note, "updated_at", datetime.utcnow())
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


@app.delete("/notes/{id}")
def remove_note(
    id: int,
    currentUser=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = db.query(Note).filter(Note.id == id).first()
    if not note:
        raise HTTPException(status_code=404, detail="note not found")

    db.delete(note)
    db.commit()

    return {"message": "note deleted", "deleted_id": id}
