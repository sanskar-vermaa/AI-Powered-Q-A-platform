from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import ai_rate_limit
from app.models import Answer, Comment, User
from app.routers.questions import get_question_or_404
from app.schemas.ai import (
    ImproveQuestionRequest,
    ImproveQuestionResponse,
    SummaryResponse,
    TagSuggestionRequest,
    TagSuggestionResponse,
)
from app.schemas.answer import AnswerOut
from app.serializers import answer_out
from app.services.ai import AIError, AIProvider, get_ai_provider
from app.services.notifications import notify

router = APIRouter(prefix="/api/ai", tags=["ai"])


def ai_unavailable(exc: AIError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))


@router.get("/status")
def ai_status(provider: AIProvider = Depends(get_ai_provider)):
    return {"provider": provider.name, "live": provider.name != "mock"}


@router.post("/questions/{question_id}/answer", response_model=AnswerOut, status_code=status.HTTP_201_CREATED)
def generate_answer(
    question_id: int,
    user: User = Depends(ai_rate_limit),
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_ai_provider),
):
    """Ask the AI to post an answer to a question. Each question gets at most one AI answer."""
    question = get_question_or_404(db, question_id)
    existing = db.scalar(select(Answer).where(Answer.question_id == question.id, Answer.is_ai.is_(True)))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This question already has an AI answer")
    try:
        body = provider.answer_question(question.title, question.body, [t.name for t in question.tags])
    except AIError as exc:
        raise ai_unavailable(exc) from exc

    answer = Answer(body=body, question_id=question.id, author_id=None, is_ai=True)
    db.add(answer)
    notify(
        db,
        question.author_id,
        "ai_answer",
        f'The AI assistant answered "{question.title}"',
        f"/questions/{question.id}",
        actor=user,
    )
    db.commit()
    db.refresh(answer)
    return answer_out(answer, question.accepted_answer_id)


@router.post("/suggest-tags", response_model=TagSuggestionResponse)
def suggest_tags(
    payload: TagSuggestionRequest, _: User = Depends(ai_rate_limit), provider: AIProvider = Depends(get_ai_provider)
):
    try:
        return TagSuggestionResponse(tags=provider.suggest_tags(payload.title, payload.body))
    except AIError as exc:
        raise ai_unavailable(exc) from exc


@router.post("/improve-question", response_model=ImproveQuestionResponse)
def improve_question(
    payload: ImproveQuestionRequest, _: User = Depends(ai_rate_limit), provider: AIProvider = Depends(get_ai_provider)
):
    try:
        return ImproveQuestionResponse(**provider.improve_question(payload.title, payload.body))
    except AIError as exc:
        raise ai_unavailable(exc) from exc


def build_thread_text(db: Session, question_id: int) -> str:
    question = get_question_or_404(db, question_id)
    parts = [question.title, "", question.body]
    for comment in db.scalars(select(Comment).where(Comment.question_id == question.id).order_by(Comment.id)):
        parts.append(f"Comment: {comment.body}")
    answers = sorted(question.answers, key=lambda a: (-a.score, a.id))
    for index, answer in enumerate(answers, start=1):
        labels = [f"score {answer.score}"]
        if answer.id == question.accepted_answer_id:
            labels.append("accepted")
        if answer.is_ai:
            labels.append("AI-generated")
        parts += ["", f"--- Answer {index} ({', '.join(labels)}) ---", answer.body]
    return "\n".join(parts)


@router.post("/questions/{question_id}/summary", response_model=SummaryResponse)
def summarize_thread(
    question_id: int,
    _: User = Depends(ai_rate_limit),
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_ai_provider),
):
    thread = build_thread_text(db, question_id)
    try:
        return SummaryResponse(summary=provider.summarize_thread(thread))
    except AIError as exc:
        raise ai_unavailable(exc) from exc
