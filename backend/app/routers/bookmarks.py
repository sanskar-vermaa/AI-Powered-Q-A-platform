from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Bookmark, User
from app.routers.questions import get_question_or_404
from app.schemas.question import QuestionSummary
from app.serializers import question_summaries

router = APIRouter(prefix="/api", tags=["bookmarks"])


@router.put("/questions/{question_id}/bookmark", status_code=status.HTTP_204_NO_CONTENT)
def add_bookmark(question_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_question_or_404(db, question_id)
    if db.get(Bookmark, {"user_id": user.id, "question_id": question_id}) is None:
        db.add(Bookmark(user_id=user.id, question_id=question_id))
        db.commit()


@router.delete("/questions/{question_id}/bookmark", status_code=status.HTTP_204_NO_CONTENT)
def remove_bookmark(question_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookmark = db.get(Bookmark, {"user_id": user.id, "question_id": question_id})
    if bookmark is not None:
        db.delete(bookmark)
        db.commit()


@router.get("/me/bookmarks", response_model=list[QuestionSummary])
def my_bookmarks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookmarks = db.scalars(
        select(Bookmark).where(Bookmark.user_id == user.id).order_by(Bookmark.created_at.desc())
    )
    return question_summaries(db, [b.question for b in bookmarks])
