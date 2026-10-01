from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.common import NullableStr


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: str
    message: str
    link: NullableStr
    is_read: bool
    created_at: datetime


class UnreadCount(BaseModel):
    unread: int
