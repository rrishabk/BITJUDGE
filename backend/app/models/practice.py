from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class PracticeProblem(TimestampMixin, Base):
    __tablename__ = "practice_problems"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    platform: Mapped[str] = mapped_column(String(32), index=True)
    difficulty: Mapped[int] = mapped_column(Integer, index=True)
    topic: Mapped[str] = mapped_column(String(120), index=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    contest_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    problem_index: Mapped[str | None] = mapped_column(String(16), nullable=True)
    link: Mapped[str] = mapped_column(String(500))


class ProblemProgress(TimestampMixin, Base):
    __tablename__ = "user_problem_progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("practice_problems.id", ondelete="CASCADE"), index=True)
    solved: Mapped[bool] = mapped_column(Boolean, default=False)
    solved_at: Mapped[datetime | None] = mapped_column(nullable=True)
