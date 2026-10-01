from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Answer, Question, Tag, User
from app.schemas.stats import LeaderboardEntry, SiteStats

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=SiteStats)
def site_stats(db: Session = Depends(get_db)):
    questions = db.scalar(select(func.count(Question.id))) or 0
    answered = db.scalar(select(func.count(Question.id)).where(Question.answers.any())) or 0
    return SiteStats(
        users=db.scalar(select(func.count(User.id))) or 0,
        questions=questions,
        answers=db.scalar(select(func.count(Answer.id))) or 0,
        ai_answers=db.scalar(select(func.count(Answer.id)).where(Answer.is_ai.is_(True))) or 0,
        tags=db.scalar(select(func.count(Tag.id))) or 0,
        answered_ratio=round(answered / questions, 3) if questions else 0.0,
    )


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
def leaderboard(db: Session = Depends(get_db), limit: int = Query(10, ge=1, le=100)):
    answer_count = (
        select(func.count(Answer.id)).where(Answer.author_id == User.id).correlate(User).scalar_subquery()
    )
    rows = db.execute(
        select(User.username, User.reputation, answer_count.label("answer_count"))
        .where(User.is_active.is_(True))
        .order_by(User.reputation.desc(), User.id)
        .limit(limit)
    ).all()
    return [LeaderboardEntry(username=r.username, reputation=r.reputation, answer_count=r.answer_count) for r in rows]
