from sqlalchemy import Identity, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(35), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default="")

    questions = relationship("Question", secondary="question_tags", back_populates="tags")
