from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    rank: int
    name: str
    problems_solved: int
    score: int
