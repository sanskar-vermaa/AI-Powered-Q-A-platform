from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.common import NullableStr

USERNAME_PATTERN = r"^[A-Za-z0-9_]{3,32}$"


class UserCreate(BaseModel):
    username: str = Field(pattern=USERNAME_PATTERN)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        if not any(c.isdigit() for c in value) or not any(c.isalpha() for c in value):
            raise ValueError("password must contain at least one letter and one digit")
        return value


class UserUpdate(BaseModel):
    bio: str | None = Field(default=None, max_length=1000)
    email: EmailStr | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    bio: NullableStr
    reputation: int
    role: str
    created_at: datetime


class UserPrivate(UserPublic):
    email: EmailStr


class UserProfile(UserPublic):
    question_count: int
    answer_count: int
    badges: list[str]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str
