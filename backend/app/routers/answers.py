from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.deps import get_current_user, get_current_user_optional
from app.models import Answer, User
from app.routers.questions import ensure_can_edit, get_question_or_404
from app.schemas.answer import AnswerCreate, AnswerOut, AnswerUpdate
from app.serializers import answer_out, user_votes
from app.services import badges
from app.services.notifications import notify

router = APIRouter(prefix="/api", tags=["answers"])


def get_answer_or_404(db: Session, answer_id: int) -> Answer:
    answer = db.get(Answer, answer_id)
    if answer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found")
    return answer


@router.get("/questions/{question_id}/answers", response_model=list[AnswerOut])
def list_answers(
    question_id: int, viewer: User | None = Depends(get_current_user_optional), db: Session = Depends(get_db)
):
    question = get_question_or_404(db, question_id)
    answers = list(
        db.scalars(select(Answer).where(Answer.question_id == question.id).options(selectinload(Answer.author)))
    )
    accepted = question.accepted_answer_id
    # Accepted answer first, then by score, then oldest first.
    answers.sort(key=lambda a: (a.id != accepted, -a.score, a.created_at, a.id))
    votes = user_votes(db, viewer, "answer", [a.id for a in answers])
    return [answer_out(a, accepted, votes.get(a.id, 0)) for a in answers]


@router.post("/questions/{question_id}/answers", response_model=AnswerOut, status_code=status.HTTP_201_CREATED)
def create_answer(
    question_id: int, payload: AnswerCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    question = get_question_or_404(db, question_id)
    answer = Answer(body=payload.body, question_id=question.id, author_id=user.id)
    db.add(answer)
    notify(
        db,
        question.author_id,
        "answer",
        f'{user.username} answered "{question.title}"',
        f"/questions/{question.id}",
        actor=user,
    )
    db.flush()
    badges.evaluate(db, user)
    db.commit()
    db.refresh(answer)
    return answer_out(answer, question.accepted_answer_id)


@router.get("/answers/{answer_id}", response_model=AnswerOut)
def get_answer(answer_id: int, db: Session = Depends(get_db)):
    answer = get_answer_or_404(db, answer_id)
    return answer_out(answer, answer.question.accepted_answer_id)


@router.patch("/answers/{answer_id}", response_model=AnswerOut)
def update_answer(
    answer_id: int, payload: AnswerUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    answer = get_answer_or_404(db, answer_id)
    if answer.is_ai and not user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="AI answers can only be edited by moderators")
    if not answer.is_ai:
        ensure_can_edit(user, answer.author_id)
    answer.body = payload.body
    db.commit()
    db.refresh(answer)
    return answer_out(answer, answer.question.accepted_answer_id)


@router.delete("/answers/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_answer(answer_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    answer = get_answer_or_404(db, answer_id)
    question = answer.question
    # The asker may remove AI answers posted to their question.
    can_delete = (
        user.is_staff
        or (answer.author_id is not None and answer.author_id == user.id)
        or (answer.is_ai and question.author_id == user.id)
    )
    if not can_delete:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only modify your own content")
    if question.accepted_answer_id == answer.id:
        question.accepted_answer_id = None
        db.flush()
    db.delete(answer)
    db.commit()
