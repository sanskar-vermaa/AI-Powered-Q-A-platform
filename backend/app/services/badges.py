"""Badge rules. Each badge is awarded at most once per user."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Answer, Question, User, UserBadge
from app.services.notifications import notify

BADGES: dict[str, str] = {
    "curious": "Asked a first question",
    "helper": "Posted a first answer",
    "teacher": "Had an answer accepted",
    "enthusiast": "Posted 10 answers",
    "popular": "A question scored 10 or more",
    "trusted": "Reached 500 reputation",
}


def _award(db: Session, user: User, badge: str, owned: set[str]) -> bool:
    if badge in owned:
        return False
    db.add(UserBadge(user_id=user.id, badge=badge))
    owned.add(badge)
    notify(db, user, "badge", f"You earned the \"{badge}\" badge: {BADGES[badge]}", f"/users/{user.username}")
    return True


def user_badges(db: Session, user_id: int) -> list[str]:
    return list(db.scalars(select(UserBadge.badge).where(UserBadge.user_id == user_id).order_by(UserBadge.id)))


def evaluate(db: Session, user: User | None) -> list[str]:
    """Award every badge `user` now qualifies for; returns the newly awarded ones."""
    if user is None:
        return []
    db.flush()
    owned = set(user_badges(db, user.id))
    awarded: list[str] = []

    question_count = db.scalar(select(func.count(Question.id)).where(Question.author_id == user.id)) or 0
    answer_count = db.scalar(select(func.count(Answer.id)).where(Answer.author_id == user.id)) or 0
    accepted = db.scalar(
        select(func.count(Answer.id))
        .join(Question, Question.accepted_answer_id == Answer.id)
        .where(Answer.author_id == user.id)
    ) or 0
    best_question = db.scalar(select(func.max(Question.score)).where(Question.author_id == user.id)) or 0

    rules = {
        "curious": question_count >= 1,
        "helper": answer_count >= 1,
        "teacher": accepted >= 1,
        "enthusiast": answer_count >= 10,
        "popular": best_question >= 10,
        "trusted": user.reputation >= 500,
    }
    for badge, earned in rules.items():
        if earned and _award(db, user, badge, owned):
            awarded.append(badge)
    return awarded
