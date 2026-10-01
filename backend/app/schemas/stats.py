from pydantic import BaseModel


class SiteStats(BaseModel):
    users: int
    questions: int
    answers: int
    ai_answers: int
    tags: int
    answered_ratio: float


class LeaderboardEntry(BaseModel):
    username: str
    reputation: int
    answer_count: int
