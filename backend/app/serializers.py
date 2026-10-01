"""Convert ORM objects into API response dictionaries."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Answer, Bookmark, Question, User, Vote
from app.utils.text import excerpt


def answer_counts(db: Session, question_ids: list[int]) -> dict[int, int]:
    if not question_ids:
        return {}
    rows = db.execute(
        select(Answer.question_id, func.count(Answer.id))
        .where(Answer.question_id.in_(question_ids))
        .group_by(Answer.question_id)
    )
    return dict(rows.all())


def user_votes(db: Session, user: User | None, target_type: str, ids: list[int]) -> dict[int, int]:
    if user is None or not ids:
        return {}
    rows = db.execute(
        select(Vote.target_id, Vote.value).where(
            Vote.user_id == user.id, Vote.target_type == target_type, Vote.target_id.in_(ids)
        )
    )
    return dict(rows.all())


def question_summaries(db: Session, questions: list[Question]) -> list[dict]:
    counts = answer_counts(db, [q.id for q in questions])
    return [
        {
            "id": q.id,
            "title": q.title,
            "excerpt": excerpt(q.body),
            "author": q.author,
            "tags": [t.name for t in q.tags],
            "score": q.score,
            "views": q.views,
            "answer_count": counts.get(q.id, 0),
            "has_accepted_answer": q.accepted_answer_id is not None,
            "created_at": q.created_at,
        }
        for q in questions
    ]


def question_detail(db: Session, question: Question, viewer: User | None) -> dict:
    my_vote = user_votes(db, viewer, "question", [question.id]).get(question.id, 0)
    bookmarked = bool(
        viewer
        and db.get(Bookmark, {"user_id": viewer.id, "question_id": question.id}) is not None
    )
    return {
        "id": question.id,
        "title": question.title,
        "body": question.body,
        "author": question.author,
        "tags": [t.name for t in question.tags],
        "score": question.score,
        "views": question.views,
        "answer_count": answer_counts(db, [question.id]).get(question.id, 0),
        "accepted_answer_id": question.accepted_answer_id,
        "created_at": question.created_at,
        "updated_at": question.updated_at,
        "my_vote": my_vote,
        "bookmarked": bookmarked,
    }


def answer_out(answer: Answer, accepted_id: int | None, my_vote: int = 0) -> dict:
    return {
        "id": answer.id,
        "question_id": answer.question_id,
        "body": answer.body,
        "author": answer.author,
        "is_ai": answer.is_ai,
        "is_accepted": answer.id == accepted_id,
        "score": answer.score,
        "created_at": answer.created_at,
        "updated_at": answer.updated_at,
        "my_vote": my_vote,
    }
