from sqlalchemy import Boolean, ForeignKey, Identity, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.mixins import TimestampMixin


class Notification(TimestampMixin, Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(32))  # answer | comment | accepted | badge | ai_answer
    message: Mapped[str] = mapped_column(String(500))
    link: Mapped[str | None] = mapped_column(String(255), nullable=True, default="")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
