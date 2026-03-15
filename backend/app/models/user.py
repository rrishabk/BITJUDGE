from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class UserRole(str, Enum):
    student = "student"
    admin = "admin"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    enrollment_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), default=UserRole.student)
    codeforces_handle: Mapped[str | None] = mapped_column(String(64), nullable=True)
    codechef_handle: Mapped[str | None] = mapped_column(String(64), nullable=True)
    leetcode_handle: Mapped[str | None] = mapped_column(String(64), nullable=True)
    hackerrank_handle: Mapped[str | None] = mapped_column(String(64), nullable=True)
    github_handle: Mapped[str | None] = mapped_column(String(64), nullable=True)


class UserStats(Base):
    __tablename__ = "user_stats"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    problems_solved: Mapped[int] = mapped_column(default=0)
    total_score: Mapped[int] = mapped_column(default=0)
    streak_days: Mapped[int] = mapped_column(default=0)
    last_submission: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
