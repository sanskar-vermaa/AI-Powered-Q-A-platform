from typing import Literal

from pydantic import BaseModel


class VoteIn(BaseModel):
    value: Literal[-1, 0, 1]


class VoteResult(BaseModel):
    score: int
    my_vote: int
