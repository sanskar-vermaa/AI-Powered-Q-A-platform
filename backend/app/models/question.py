from sqlalchemy import Column, ForeignKey, Identity, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin

question_tags = Table(
    "question_tags",
    Base.metadata,
    Column("question_id", ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Question(TimestampMixin, Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    body: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[int] = mapped_column(Integer, default=0)
    accepted_answer_id: Mapped[int | None] = mapped_column(
        ForeignKey("answers.id", use_alter=True, ondelete="SET NULL"), nullable=True
    )

    author = relationship("User", back_populates="questions")
    tags = relationship("Tag", secondary=question_tags, back_populates="questions", order_by="Tag.name")
    answers = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
        foreign_keys="Answer.question_id",
    )
    comments = relationship("Comment", back_populates="question", cascade="all, delete-orphan")
