from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.quiz import QuestionType, SubmissionStatus

SUPPORTED_LANGUAGES = {
    "c++": "cpp",
    "cpp": "cpp",
    "c": "c",
    "java": "java",
    "python": "python",
    "python3": "python",
}


class QuizCreate(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    number_of_questions: int
    is_published: bool = True


class QuizOut(BaseModel):
    id: int
    title: str
    start_time: datetime
    end_time: datetime
    number_of_questions: int
    is_published: bool

    model_config = {"from_attributes": True}


class MCQCreate(BaseModel):
    question: str
    options: list[str] = Field(min_length=2)
    correct_answer: str
    topic: str


class CodingQuestionCreate(BaseModel):
    question: str
    sample_input: str
    sample_output: str
    testcases: list[dict] = Field(min_length=1)
    languages: list[str] = Field(min_length=1)
    topic: str

    @field_validator("languages", mode="before")
    @classmethod
    def normalize_languages(cls, values: list[str]) -> list[str]:
        normalized = []
        for value in values:
            key = str(value).strip().lower()
            if key not in SUPPORTED_LANGUAGES:
                raise ValueError("Supported languages are C++, C, Java, and Python")
            normalized.append(SUPPORTED_LANGUAGES[key])
        return normalized


class QuizQuestionAttach(BaseModel):
    quiz_id: int
    question_type: QuestionType
    question_id: int
    order_index: int


class SubmissionCreate(BaseModel):
    quiz_id: int | None = None
    question_type: QuestionType
    mcq_question_id: int | None = None
    coding_question_id: int | None = None
    selected_option: str | None = None
    source_code: str | None = None
    language: str | None = None

    @field_validator("language")
    @classmethod
    def normalize_language(cls, value: str | None) -> str | None:
        if value is None:
            return value
        key = value.strip().lower()
        if key not in SUPPORTED_LANGUAGES:
            raise ValueError("Supported languages are C++, C, Java, and Python")
        return SUPPORTED_LANGUAGES[key]

    @model_validator(mode="after")
    def validate_submission(self) -> "SubmissionCreate":
        if self.question_type == QuestionType.mcq:
            if not self.mcq_question_id or not self.selected_option:
                raise ValueError("MCQ submission requires mcq_question_id and selected_option")
        if self.question_type == QuestionType.coding:
            if not self.coding_question_id or not self.source_code or not self.language:
                raise ValueError("Coding submission requires coding_question_id, source_code, and language")
        return self


class SubmissionOut(BaseModel):
    id: int
    question_type: QuestionType
    verdict: str
    status: SubmissionStatus
    score: int
    execution_time: str | None
    memory_used: int | None
    verdict_payload: dict | None

    model_config = {"from_attributes": True}
