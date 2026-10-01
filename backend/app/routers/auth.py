from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas.user import LoginRequest, PasswordChange, Token, UserCreate, UserPrivate
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _authenticate(db: Session, username: str, password: str) -> User:
    user = db.scalar(
        select(User).where(or_(func.lower(User.username) == username.lower(), func.lower(User.email) == username.lower()))
    )
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is suspended")
    return user


@router.post("/register", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(func.lower(User.username) == payload.username.lower())):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username is already taken")
    if db.scalar(select(User).where(func.lower(User.email) == payload.email.lower())):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

    # The first account on a fresh install becomes the administrator.
    is_first = db.scalar(select(func.count(User.id))) == 0
    user = User(
        username=payload.username,
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
        role="admin" if is_first else "user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = _authenticate(db, payload.username, payload.password)
    return Token(access_token=create_access_token(user.id))


@router.post("/token", response_model=Token, include_in_schema=False)
def token(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 password flow endpoint used by the interactive API docs."""
    user = _authenticate(db, form.username, form.password)
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserPrivate)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(payload: PasswordChange, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
