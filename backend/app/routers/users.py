from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, true
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Answer, Question, User
from app.schemas.answer import AnswerOut
from app.schemas.user import UserPrivate, UserProfile, UserPublic, UserUpdate
from app.serializers import answer_out
from app.services.badges import user_badges

router = APIRouter(prefix="/api/users", tags=["users"])


def get_user_by_username(db: Session, username: str) -> User:
    user = db.scalar(select(User).where(func.lower(User.username) == username.lower()))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("", response_model=list[UserPublic])
def list_users(
    db: Session = Depends(get_db),
    q: str | None = Query(None, max_length=32),
    limit: int = Query(30, ge=1, le=100),
):
    stmt = select(User).where(User.is_active == true())
    if q:
        stmt = stmt.where(User.username.ilike(f"%{q}%"))
    return list(db.scalars(stmt.order_by(User.reputation.desc(), User.id).limit(limit)))


@router.patch("/me", response_model=UserPrivate)
def update_me(payload: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.email is not None and payload.email.lower() != user.email:
        if db.scalar(select(User).where(func.lower(User.email) == payload.email.lower())):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")
        user.email = payload.email.lower()
    if payload.bio is not None:
        user.bio = payload.bio
    db.commit()
    db.refresh(user)
    return user


@router.get("/{username}", response_model=UserProfile)
def get_profile(username: str, db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    return {
        **UserPublic.model_validate(user).model_dump(),
        "question_count": db.scalar(select(func.count(Question.id)).where(Question.author_id == user.id)) or 0,
        "answer_count": db.scalar(select(func.count(Answer.id)).where(Answer.author_id == user.id)) or 0,
        "badges": user_badges(db, user.id),
    }


@router.get("/{username}/answers", response_model=list[AnswerOut])
def user_answers(username: str, db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=100)):
    user = get_user_by_username(db, username)
    answers = db.scalars(
        select(Answer)
        .where(Answer.author_id == user.id)
        .order_by(Answer.created_at.desc(), Answer.id.desc())
        .limit(limit)
    )
    return [answer_out(a, a.question.accepted_answer_id) for a in answers]
