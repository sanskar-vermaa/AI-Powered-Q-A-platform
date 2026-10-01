from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_access_token
from app.utils.rate_limit import RateLimiter

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)

# AI calls are the expensive ones, so they are rate limited per user.
ai_rate_limiter = RateLimiter(limit=20, window_seconds=60)


def _user_from_token(db: Session, token: str | None) -> User | None:
    if not token:
        return None
    subject = decode_access_token(token)
    if subject is None or not subject.isdigit():
        return None
    user = db.get(User, int(subject))
    if user is None or not user.is_active:
        return None
    return user


def get_current_user_optional(token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User | None:
    return _user_from_token(db, token)


def get_current_user(token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user = _user_from_token(db, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_staff(user: User = Depends(get_current_user)) -> User:
    if not user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Moderator privileges required")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return user


def ai_rate_limit(request: Request, user: User = Depends(get_current_user)) -> User:
    if not ai_rate_limiter.allow(f"user:{user.id}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="AI rate limit exceeded, try again soon"
        )
    return user
