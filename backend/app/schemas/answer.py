from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.user import UserPublic


class AnswerCreate(BaseModel):
    body: str = Field(min_length=20, max_length=30000)


class AnswerUpdate(BaseModel):
    body: str = Field(min_length=20, max_length=30000)


class AnswerOut(BaseModel):
    id: int
    question_id: int
    body: str
    author: UserPublic | None
    is_ai: bool
    is_accepted: bool
    score: int
    created_at: datetime
    updated_at: datetime
    my_vote: int = 0
