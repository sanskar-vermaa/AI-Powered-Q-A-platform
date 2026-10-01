from sqlalchemy import ForeignKey, Identity, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin


class Flag(TimestampMixin, Base):
    __tablename__ = "flags"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    target_type: Mapped[str] = mapped_column(String(16))  # question | answer | comment
    target_id: Mapped[int] = mapped_column(Integer, index=True)
    reason: Mapped[str] = mapped_column(String(32))  # spam | offensive | off_topic | other
    details: Mapped[str | None] = mapped_column(Text, nullable=True, default="")
    status: Mapped[str] = mapped_column(String(16), default="open")  # open | resolved | dismissed

    reporter = relationship("User")
