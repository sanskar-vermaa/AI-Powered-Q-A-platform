from sqlalchemy import Boolean, ForeignKey, Identity, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin


class Answer(TimestampMixin, Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    body: Mapped[str] = mapped_column(Text)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    # AI-generated answers have no human author.
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_ai: Mapped[bool] = mapped_column(Boolean, default=False)
    score: Mapped[int] = mapped_column(Integer, default=0)

    question = relationship("Question", back_populates="answers", foreign_keys=[question_id])
    author = relationship("User", back_populates="answers")
    comments = relationship("Comment", back_populates="answer", cascade="all, delete-orphan")
