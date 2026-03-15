from pydantic import BaseModel


class PracticeProblemOut(BaseModel):
    id: int
    title: str
    platform: str
    link: str
    difficulty: int
    topic: str
    solved: bool = False


class ProblemProgressUpdate(BaseModel):
    problem_id: int
    solved: bool = True


class ProblemProgressResponse(BaseModel):
    problem_id: int
    solved: bool
    total_solved: int
    remaining_problems: int
