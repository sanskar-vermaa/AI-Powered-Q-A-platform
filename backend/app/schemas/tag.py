from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import NullableStr


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: NullableStr


class TagWithCount(TagOut):
    question_count: int


class TagUpdate(BaseModel):
    description: str = Field(max_length=2000)
