from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class QuestionType(str, Enum):
    mcq = "mcq"
    coding = "coding"


class SubmissionStatus(str, Enum):
    pending = "pending"
    running = "running"
    accepted = "accepted"
    wrong_answer = "wrong_answer"
    compilation_error = "compilation_error"
    runtime_error = "runtime_error"


class Quiz(TimestampMixin, Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    number_of_questions: Mapped[int] = mapped_column(Integer)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)


class MCQQuestion(TimestampMixin, Base):
    __tablename__ = "mcq_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(Text)
    options: Mapped[list[str]] = mapped_column(JSON)
    correct_answer: Mapped[str] = mapped_column(String(255))
    topic: Mapped[str] = mapped_column(String(120))


class CodingQuestion(TimestampMixin, Base):
    __tablename__ = "coding_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(Text)
    sample_input: Mapped[str] = mapped_column(Text)
    sample_output: Mapped[str] = mapped_column(Text)
    testcases: Mapped[list[dict]] = mapped_column(JSON)
    languages: Mapped[list[str]] = mapped_column(JSON)
    topic: Mapped[str] = mapped_column(String(120))


class QuizQuestionLink(TimestampMixin, Base):
    __tablename__ = "quiz_question_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), index=True)
    question_type: Mapped[QuestionType] = mapped_column(SqlEnum(QuestionType))
    question_id: Mapped[int] = mapped_column(Integer)
    order_index: Mapped[int] = mapped_column(Integer)


class QuizAttempt(TimestampMixin, Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    score: Mapped[int] = mapped_column(Integer, default=0)
    answers: Mapped[dict] = mapped_column(JSON, default=dict)


class Submission(TimestampMixin, Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    quiz_id: Mapped[int | None] = mapped_column(ForeignKey("quizzes.id", ondelete="SET NULL"), nullable=True)
    question_type: Mapped[QuestionType] = mapped_column(SqlEnum(QuestionType))
    mcq_question_id: Mapped[int | None] = mapped_column(ForeignKey("mcq_questions.id", ondelete="SET NULL"), nullable=True)
    coding_question_id: Mapped[int | None] = mapped_column(ForeignKey("coding_questions.id", ondelete="SET NULL"), nullable=True)
    source_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    selected_option: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[SubmissionStatus] = mapped_column(SqlEnum(SubmissionStatus), default=SubmissionStatus.pending)
    score: Mapped[int] = mapped_column(Integer, default=0)
    execution_time: Mapped[str | None] = mapped_column(String(32), nullable=True)
    memory_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    judge0_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    verdict_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
