import jwt
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import ALGORITHM, SECRET
from app.core.security import get_password_hash, make_token, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginBody,
    LoginResponse,
    RegisterBody,
    RegisteredUserPublic,
    RegisterResponse,
    UserPublic,
)

router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
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
        token_claims = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        user_id = token_claims.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="bad token")
    except Exception as exc:
        raise HTTPException(status_code=401, detail="invalid token") from exc

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="user not found")
    return user


@router.post("/register", response_model=RegisterResponse)
def register(
    body: RegisterBody, db: Session = Depends(get_db)
) -> RegisterResponse:
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="email already used")

    user = User(
        name=body.name,
        email=body.email,
        password=get_password_hash(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return RegisterResponse(
        message="register success",
        user=RegisteredUserPublic.model_validate(user, from_attributes=True),
    )


@router.post("/login", response_model=LoginResponse)
def login(
    login_body: LoginBody, db: Session = Depends(get_db)
) -> LoginResponse:
    user = db.query(User).filter(User.email == login_body.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="email/password salah")

    if not verify_password(login_body.password, str(user.password)):
        raise HTTPException(status_code=401, detail="email/password salah")

    token = make_token({"user_id": user.id, "email": user.email})
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserPublic.model_validate(user, from_attributes=True),
    )
