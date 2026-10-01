from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import NullableStr
from app.schemas.user import UserPublic


class FlagCreate(BaseModel):
    target_type: Literal["question", "answer", "comment"]
    target_id: int
    reason: Literal["spam", "offensive", "off_topic", "other"]
    details: str = Field(default="", max_length=1000)


class FlagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reporter: UserPublic
    target_type: str
    target_id: int
    reason: str
    details: NullableStr
    status: str
    created_at: datetime


class FlagResolve(BaseModel):
    status: Literal["resolved", "dismissed"]
    delete_content: bool = False
