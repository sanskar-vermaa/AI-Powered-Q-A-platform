from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserPublic


class CommentCreate(BaseModel):
    body: str = Field(min_length=2, max_length=600)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    body: str
    author: UserPublic
    question_id: int | None
    answer_id: int | None
    created_at: datetime
