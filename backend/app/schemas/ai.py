from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TagSuggestionRequest(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    body: str = Field(default="", max_length=30000)


class TagSuggestionResponse(BaseModel):
    tags: list[str]


class ImproveQuestionRequest(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    body: str = Field(min_length=10, max_length=30000)


class ImproveQuestionResponse(BaseModel):
    title: str
    body: str
    tips: list[str]


class SummaryResponse(BaseModel):
    summary: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    conversation_id: int | None = None


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    created_at: datetime


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationDetail(ConversationOut):
    messages: list[ChatMessageOut]


class ChatResponse(BaseModel):
    conversation_id: int
    reply: ChatMessageOut
