from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Question
from app.utils.text import jaccard, tokenize


def find_similar(db: Session, title: str, body: str = "", exclude_id: int | None = None, limit: int = 5,
                 threshold: float = 0.15) -> list[tuple[Question, float]]:
    """Rank existing questions by keyword overlap with the given text (used for duplicate detection)."""
    title_tokens = tokenize(title)
    query_tokens = title_tokens | tokenize(body)
    if not title_tokens:
        return []

    filters = [Question.title.ilike(f"%{token}%") for token in sorted(title_tokens)[:10]]
    stmt = select(Question).where(or_(*filters)).limit(200)
    if exclude_id is not None:
        stmt = stmt.where(Question.id != exclude_id)

    scored: list[tuple[Question, float]] = []
    for question in db.scalars(stmt):
        candidate = tokenize(question.title)
        # Titles carry most of the signal; bodies add a little context.
        score = 0.8 * jaccard(title_tokens, candidate) + 0.2 * jaccard(query_tokens, candidate | tokenize(question.body))
        if score >= threshold:
            scored.append((question, round(score, 3)))
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:limit]
