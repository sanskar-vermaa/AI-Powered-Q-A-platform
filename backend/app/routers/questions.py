from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.database import get_db
from app.deps import get_current_user, get_current_user_optional
from app.models import Answer, Question, Tag, User
from app.schemas.question import QuestionCreate, QuestionDetail, QuestionSummary, QuestionUpdate, SimilarQuestion
from app.serializers import question_detail, question_summaries
from app.services import badges
from app.services.search import find_similar
from app.services.tags import get_or_create_tags
from app.utils.pagination import Page, make_page

router = APIRouter(prefix="/api/questions", tags=["questions"])

SortOption = Literal["newest", "votes", "views", "unanswered", "active"]


def get_question_or_404(db: Session, question_id: int) -> Question:
    question = db.get(Question, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return question


def ensure_can_edit(user: User, owner_id: int | None) -> None:
    if owner_id != user.id and not user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only modify your own content")


@router.get("", response_model=Page[QuestionSummary])
def list_questions(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int | None = Query(None, ge=1),
    sort: SortOption = "newest",
    tag: str | None = None,
    q: str | None = Query(None, max_length=200),
    author: str | None = None,
):
    settings = get_settings()
    size = min(page_size or settings.default_page_size, settings.max_page_size)

    stmt = select(Question)
    if tag:
        stmt = stmt.where(Question.tags.any(Tag.name == tag.lower()))
    if author:
        stmt = stmt.join(User, Question.author_id == User.id).where(func.lower(User.username) == author.lower())
    if q:
        for term in q.split()[:8]:
            like = f"%{term}%"
            stmt = stmt.where(or_(Question.title.ilike(like), Question.body.ilike(like)))
    if sort == "unanswered":
        stmt = stmt.where(~Question.answers.any())

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    order = {
        "newest": [Question.created_at.desc()],
        "votes": [Question.score.desc(), Question.created_at.desc()],
        "views": [Question.views.desc(), Question.created_at.desc()],
        "unanswered": [Question.created_at.desc()],
        "active": [Question.updated_at.desc()],
    }[sort]
    stmt = (
        stmt.options(selectinload(Question.tags), selectinload(Question.author))
        .order_by(*order, Question.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    questions = list(db.scalars(stmt))
    return make_page(question_summaries(db, questions), total, page, size)


@router.post("", response_model=QuestionDetail, status_code=status.HTTP_201_CREATED)
def create_question(payload: QuestionCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    question = Question(title=payload.title.strip(), body=payload.body, author_id=user.id)
    question.tags = get_or_create_tags(db, payload.tags)
    db.add(question)
    db.flush()
    badges.evaluate(db, user)
    db.commit()
    db.refresh(question)
    return question_detail(db, question, user)


@router.get("/similar", response_model=list[SimilarQuestion])
def similar_questions(
    title: str = Query(min_length=3, max_length=200),
    body: str = Query("", max_length=5000),
    db: Session = Depends(get_db),
):
    """Find existing questions that look like duplicates of a draft."""
    return [{"id": q.id, "title": q.title, "score": score} for q, score in find_similar(db, title, body)]


@router.get("/{question_id}", response_model=QuestionDetail)
def get_question(
    question_id: int,
    count_view: bool = True,
    viewer: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    question = get_question_or_404(db, question_id)
    if count_view:
        # Bump the counter in SQL so concurrent views don't overwrite each other or touch updated_at.
        db.execute(Question.__table__.update().where(Question.id == question_id).values(views=Question.views + 1))
        db.commit()
        db.refresh(question)
    return question_detail(db, question, viewer)


@router.get("/{question_id}/related", response_model=list[SimilarQuestion])
def related_questions(question_id: int, db: Session = Depends(get_db)):
    question = get_question_or_404(db, question_id)
    matches = find_similar(db, question.title, question.body, exclude_id=question.id, threshold=0.05)
    return [{"id": q.id, "title": q.title, "score": score} for q, score in matches]


@router.patch("/{question_id}", response_model=QuestionDetail)
def update_question(
    question_id: int, payload: QuestionUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    question = get_question_or_404(db, question_id)
    ensure_can_edit(user, question.author_id)
    if payload.title is not None:
        question.title = payload.title.strip()
    if payload.body is not None:
        question.body = payload.body
    if payload.tags is not None:
        question.tags = get_or_create_tags(db, payload.tags)
    db.commit()
    db.refresh(question)
    return question_detail(db, question, user)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(question_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    question = get_question_or_404(db, question_id)
    ensure_can_edit(user, question.author_id)
    question.accepted_answer_id = None
    db.flush()
    db.delete(question)
    db.commit()


@router.post("/{question_id}/accept/{answer_id}", response_model=QuestionDetail)
def accept_answer(
    question_id: int, answer_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    from app.services import reputation
    from app.services.notifications import notify

    question = get_question_or_404(db, question_id)
    if question.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only the question author can accept an answer"
        )
    answer = db.get(Answer, answer_id)
    if answer is None or answer.question_id != question.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found on this question")

    previous_id = question.accepted_answer_id
    if previous_id == answer.id:
        # Accepting the accepted answer again toggles acceptance off.
        question.accepted_answer_id = None
        if answer.author_id != user.id:
            reputation.adjust(db, answer.author, -reputation.ANSWER_ACCEPTED)
            reputation.adjust(db, user, -reputation.ACCEPTING_ANSWER)
    else:
        if previous_id is not None:
            previous = db.get(Answer, previous_id)
            if previous is not None and previous.author_id != user.id:
                reputation.adjust(db, previous.author, -reputation.ANSWER_ACCEPTED)
                reputation.adjust(db, user, -reputation.ACCEPTING_ANSWER)
        question.accepted_answer_id = answer.id
        if answer.author_id != user.id:
            reputation.adjust(db, answer.author, reputation.ANSWER_ACCEPTED)
            reputation.adjust(db, user, reputation.ACCEPTING_ANSWER)
        notify(
            db,
            answer.author,
            "accepted",
            f'Your answer to "{question.title}" was accepted',
            f"/questions/{question.id}",
            actor=user,
        )
        badges.evaluate(db, answer.author)
    db.commit()
    db.refresh(question)
    return question_detail(db, question, user)
