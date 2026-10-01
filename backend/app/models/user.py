from sqlalchemy import Boolean, Identity, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(Text, nullable=True, default="")
    reputation: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String(16), default="user")  # "user" | "moderator" | "admin"

    questions = relationship("Question", back_populates="author", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="author")

    @property
    def is_staff(self) -> bool:
        return self.role in ("moderator", "admin")
