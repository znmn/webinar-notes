import jwt
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import ALGORITHM, SECRET
from app.core.security import make_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginBody, RegisterBody

router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    db: Session = Depends(get_db),
):
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="missing authorization header",
        )
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="invalid authorization format",
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        uid = payload.get("user_id")
        if uid is None:
            raise HTTPException(status_code=401, detail="bad token")
    except Exception as exc:
        raise HTTPException(status_code=401, detail="invalid token") from exc

    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=401, detail="user not found")
    return user


@router.post("/register")
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


@router.post("/login")
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
