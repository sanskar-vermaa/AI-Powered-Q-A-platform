import json
from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.deps import ai_rate_limit, get_current_user
from app.models import ChatMessage, Conversation, User
from app.models.mixins import utcnow
from app.routers.ai import ai_unavailable
from app.schemas.ai import ChatRequest, ChatResponse, ConversationDetail, ConversationOut
from app.services.ai import AIError, AIProvider, ChatTurn, get_ai_provider
from app.utils.text import excerpt

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Only the most recent messages are sent to the model to bound request size.
HISTORY_LIMIT = 30


def _get_conversation(db: Session, user: User, conversation_id: int) -> Conversation:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None or conversation.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


def _start_turn(db: Session, user: User, payload: ChatRequest) -> tuple[Conversation, list[ChatTurn]]:
    if payload.conversation_id is None:
        conversation = Conversation(user_id=user.id, title=excerpt(payload.message, 80))
        db.add(conversation)
        db.flush()
    else:
        conversation = _get_conversation(db, user, payload.conversation_id)
    db.add(ChatMessage(conversation_id=conversation.id, role="user", content=payload.message))
    db.commit()
    db.refresh(conversation)
    history = merge_turns([ChatTurn(m.role, m.content) for m in conversation.messages[-HISTORY_LIMIT:]])
    return conversation, history


def merge_turns(turns: list[ChatTurn]) -> list[ChatTurn]:
    """Join consecutive messages from the same role and drop a leading assistant turn.

    A failed AI call leaves a user message without a reply, so the stored history can
    contain back-to-back user messages; the model expects alternating roles.
    """
    merged: list[ChatTurn] = []
    for turn in turns:
        if merged and merged[-1].role == turn.role:
            merged[-1] = ChatTurn(turn.role, f"{merged[-1].content}\n\n{turn.content}")
        else:
            merged.append(turn)
    while merged and merged[0].role != "user":
        merged.pop(0)
    return merged


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(Conversation).where(Conversation.user_id == user.id).order_by(Conversation.updated_at.desc())
    return list(db.scalars(stmt))


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _get_conversation(db, user, conversation_id)


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(_get_conversation(db, user, conversation_id))
    db.commit()


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    user: User = Depends(ai_rate_limit),
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_ai_provider),
):
    conversation, history = _start_turn(db, user, payload)
    try:
        reply_text = provider.chat(history)
    except AIError as exc:
        raise ai_unavailable(exc) from exc
    reply = ChatMessage(conversation_id=conversation.id, role="assistant", content=reply_text)
    db.add(reply)
    conversation.updated_at = utcnow()
    db.commit()
    db.refresh(reply)
    return ChatResponse(conversation_id=conversation.id, reply=reply)


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("/stream")
def chat_stream(
    payload: ChatRequest,
    user: User = Depends(ai_rate_limit),
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_ai_provider),
):
    """Stream the assistant reply as server-sent events: `start`, `delta`*, then `done` or `error`."""
    conversation, history = _start_turn(db, user, payload)
    conversation_id = conversation.id

    def events() -> Iterator[str]:
        yield _sse("start", {"conversation_id": conversation_id})
        chunks: list[str] = []
        try:
            for chunk in provider.stream_chat(history):
                chunks.append(chunk)
                yield _sse("delta", {"text": chunk})
        except AIError as exc:
            yield _sse("error", {"detail": str(exc)})
            return
        # The request-scoped session is closed once the response starts, so use a fresh one.
        with SessionLocal() as session:
            message = ChatMessage(conversation_id=conversation_id, role="assistant", content="".join(chunks).strip())
            session.add(message)
            stored = session.get(Conversation, conversation_id)
            if stored is not None:
                stored.updated_at = utcnow()
            session.commit()
            yield _sse("done", {"message_id": message.id})

    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})
