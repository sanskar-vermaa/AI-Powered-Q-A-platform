from sqlalchemy import ForeignKey, Identity, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin


class Comment(TimestampMixin, Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    body: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    question_id: Mapped[int | None] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=True)
    answer_id: Mapped[int | None] = mapped_column(ForeignKey("answers.id", ondelete="CASCADE"), nullable=True)

    author = relationship("User")
    question = relationship("Question", back_populates="comments")
    answer = relationship("Answer", back_populates="comments")
