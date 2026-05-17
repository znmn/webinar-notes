import jwt
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import ALGORITHM, SECRET
from app.core.logger import get_logger
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
logger = get_logger(__name__)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate bearer token and return the authenticated user."""
    if not credentials:
        logger.warning("Missing authorization header")
        raise HTTPException(
            status_code=401,
            detail="missing authorization header",
        )
    if credentials.scheme.lower() != "bearer":
        logger.warning(
            "Invalid authorization format: scheme=%s",
            credentials.scheme,
        )
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
    except jwt.InvalidTokenError as exc:
        logger.warning("Invalid token received")
        raise HTTPException(status_code=401, detail="invalid token") from exc

    try:
        user = db.query(User).filter(User.id == user_id).first()
    except SQLAlchemyError as exc:
        logger.exception("Database error while fetching current user")
        raise HTTPException(
            status_code=500, detail="internal server error"
        ) from exc
    if not user:
        logger.warning("User not found for token user_id=%s", user_id)
        raise HTTPException(status_code=401, detail="user not found")
    return user


@router.post("/register", response_model=RegisterResponse)
def register(
    body: RegisterBody, db: Session = Depends(get_db)
) -> RegisterResponse:
    """Register a new user account."""
    try:
        existing = db.query(User).filter(User.email == body.email).first()
        if existing:
            logger.info(
                "Registration blocked, email already used: %s", body.email
            )
            raise HTTPException(status_code=400, detail="email already used")

        user = User(
            name=body.name,
            email=body.email,
            password=get_password_hash(body.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("User registered successfully: user_id=%s", user.id)
        return RegisterResponse(
            message="register success",
            user=RegisteredUserPublic.model_validate(
                user, from_attributes=True
            ),
        )
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Database error during registration")
        raise HTTPException(
            status_code=500, detail="internal server error"
        ) from exc


@router.post("/login", response_model=LoginResponse)
def login(
    login_body: LoginBody, db: Session = Depends(get_db)
) -> LoginResponse:
    """Authenticate user credentials and return an access token."""
    try:
        user = db.query(User).filter(User.email == login_body.email).first()
    except SQLAlchemyError as exc:
        logger.exception("Database error during login lookup")
        raise HTTPException(
            status_code=500, detail="internal server error"
        ) from exc
    if not user:
        logger.info("Login failed, email not found: %s", login_body.email)
        raise HTTPException(status_code=401, detail="email/password salah")

    if not verify_password(login_body.password, str(user.password)):
        logger.info(
            "Login failed, invalid password for email: %s", login_body.email
        )
        raise HTTPException(status_code=401, detail="email/password salah")

    token = make_token({"user_id": user.id, "email": user.email})
    logger.info("Login success: user_id=%s", user.id)
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserPublic.model_validate(user, from_attributes=True),
    )
