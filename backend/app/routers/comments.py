from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models import Comment, User
from app.routers.answers import get_answer_or_404
from app.routers.questions import ensure_can_edit, get_question_or_404
from app.schemas.comment import CommentCreate, CommentOut
from app.services.notifications import notify

router = APIRouter(prefix="/api", tags=["comments"])


@router.get("/questions/{question_id}/comments", response_model=list[CommentOut])
def list_question_comments(question_id: int, db: Session = Depends(get_db)):
    get_question_or_404(db, question_id)
    stmt = select(Comment).where(Comment.question_id == question_id).options(selectinload(Comment.author))
    return list(db.scalars(stmt.order_by(Comment.id)))


@router.post("/questions/{question_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def comment_on_question(
    question_id: int, payload: CommentCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    question = get_question_or_404(db, question_id)
    comment = Comment(body=payload.body, author_id=user.id, question_id=question.id)
    db.add(comment)
    notify(
        db,
        question.author_id,
        "comment",
        f'{user.username} commented on "{question.title}"',
        f"/questions/{question.id}",
        actor=user,
    )
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/answers/{answer_id}/comments", response_model=list[CommentOut])
def list_answer_comments(answer_id: int, db: Session = Depends(get_db)):
    get_answer_or_404(db, answer_id)
    stmt = select(Comment).where(Comment.answer_id == answer_id).options(selectinload(Comment.author))
    return list(db.scalars(stmt.order_by(Comment.id)))


@router.post("/answers/{answer_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def comment_on_answer(
    answer_id: int, payload: CommentCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    answer = get_answer_or_404(db, answer_id)
    comment = Comment(body=payload.body, author_id=user.id, answer_id=answer.id)
    db.add(comment)
    notify(
        db,
        answer.author_id,
        "comment",
        f"{user.username} commented on your answer",
        f"/questions/{answer.question_id}",
        actor=user,
    )
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    comment = db.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    ensure_can_edit(user, comment.author_id)
    db.delete(comment)
    db.commit()
