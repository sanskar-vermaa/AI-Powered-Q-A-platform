from sqlalchemy.orm import Session

from app.models import User

# Points awarded (or removed) for community actions.
QUESTION_UPVOTE = 5
ANSWER_UPVOTE = 10
DOWNVOTE_RECEIVED = -2
ANSWER_ACCEPTED = 15
ACCEPTING_ANSWER = 2
MIN_REPUTATION = 1


def vote_delta(target_type: str, value: int) -> int:
    """Reputation change for the content author when a vote of `value` is cast."""
    if value > 0:
        return QUESTION_UPVOTE if target_type == "question" else ANSWER_UPVOTE
    if value < 0:
        return DOWNVOTE_RECEIVED
    return 0


def adjust(db: Session, user: User | None, delta: int) -> None:
    if user is None or delta == 0:
        return
    user.reputation = max(MIN_REPUTATION, user.reputation + delta)
    db.add(user)
