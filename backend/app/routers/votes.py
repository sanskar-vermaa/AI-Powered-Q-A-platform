from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Answer, Question, User, Vote
from app.schemas.vote import VoteIn, VoteResult
from app.services import badges, reputation

router = APIRouter(prefix="/api", tags=["votes"])


def _apply_vote(db: Session, user: User, target_type: str, target: Question | Answer, value: int) -> VoteResult:
    if target.author_id == user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot vote on your own post")

    vote = db.scalar(
        select(Vote).where(Vote.user_id == user.id, Vote.target_type == target_type, Vote.target_id == target.id)
    )
    previous = vote.value if vote else 0
    if previous == value:
        return VoteResult(score=target.score, my_vote=value)

    author = target.author
    # Undo the reputation effect of the previous vote, then apply the new one.
    reputation.adjust(db, author, -reputation.vote_delta(target_type, previous))
    reputation.adjust(db, author, reputation.vote_delta(target_type, value))
    target.score += value - previous

    if value == 0:
        db.delete(vote)
    elif vote is None:
        db.add(Vote(user_id=user.id, target_type=target_type, target_id=target.id, value=value))
    else:
        vote.value = value
    badges.evaluate(db, author)
    db.commit()
    return VoteResult(score=target.score, my_vote=value)


@router.post("/questions/{question_id}/vote", response_model=VoteResult)
def vote_question(question_id: int, payload: VoteIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    question = db.get(Question, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return _apply_vote(db, user, "question", question, payload.value)


@router.post("/answers/{answer_id}/vote", response_model=VoteResult)
def vote_answer(answer_id: int, payload: VoteIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    answer = db.get(Answer, answer_id)
    if answer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found")
    return _apply_vote(db, user, "answer", answer, payload.value)
