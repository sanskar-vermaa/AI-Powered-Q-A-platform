from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserPublic


class QuestionBase(BaseModel):
    title: str = Field(min_length=10, max_length=200)
    body: str = Field(min_length=20, max_length=30000)
    tags: list[str] = Field(default_factory=list, max_length=5)


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=10, max_length=200)
    body: str | None = Field(default=None, min_length=20, max_length=30000)
    tags: list[str] | None = Field(default=None, max_length=5)


class QuestionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    excerpt: str
    author: UserPublic
    tags: list[str]
    score: int
    views: int
    answer_count: int
    has_accepted_answer: bool
    created_at: datetime


class QuestionDetail(BaseModel):
    id: int
    title: str
    body: str
    author: UserPublic
    tags: list[str]
    score: int
    views: int
    answer_count: int
    accepted_answer_id: int | None
    created_at: datetime
    updated_at: datetime
    my_vote: int = 0
    bookmarked: bool = False


class SimilarQuestion(BaseModel):
    id: int
    title: str
    score: float
