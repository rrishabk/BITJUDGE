from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.practice import ProblemProgress, PracticeProblem
from app.models.quiz import Submission
from app.models.user import UserStats
from app.services.cache import delete_cache_keys


async def ensure_user_stats(db: AsyncSession, user_id: int) -> UserStats:
    stats = await db.get(UserStats, user_id)
    if stats is None:
        stats = UserStats(user_id=user_id, problems_solved=0, total_score=0, streak_days=0)
        db.add(stats)
        await db.flush()
    return stats


async def refresh_user_stats(db: AsyncSession, user_id: int) -> UserStats:
    stats = await ensure_user_stats(db, user_id)

    problems_solved = await db.scalar(
        select(func.count()).select_from(ProblemProgress).where(
            ProblemProgress.user_id == user_id,
            ProblemProgress.solved.is_(True),
        )
    )
    total_score = await db.scalar(
        select(func.coalesce(func.sum(Submission.score), 0)).where(Submission.user_id == user_id)
    )

    solved_dates = (
        await db.execute(
            select(ProblemProgress.solved_at).where(
                ProblemProgress.user_id == user_id,
                ProblemProgress.solved.is_(True),
                ProblemProgress.solved_at.is_not(None),
            )
        )
    ).scalars().all()
    submission_dates = (
        await db.execute(
            select(Submission.created_at).where(Submission.user_id == user_id)
        )
    ).scalars().all()

    activity_dates = sorted(
        {
            dt.astimezone(timezone.utc).date() if isinstance(dt, datetime) else dt
            for dt in [*solved_dates, *submission_dates]
            if dt is not None
        },
        reverse=True,
    )

    streak_days = 0
    if activity_dates:
        current = activity_dates[0]
        today = datetime.now(timezone.utc).date()
        if current == today or current == today - timedelta(days=1):
            streak_days = 1
            previous = current
            for activity_day in activity_dates[1:]:
                if activity_day == previous - timedelta(days=1):
                    streak_days += 1
                    previous = activity_day
                elif activity_day == previous:
                    continue
                else:
                    break

    last_submission = max(submission_dates) if submission_dates else max(solved_dates) if solved_dates else None

    stats.problems_solved = int(problems_solved or 0)
    stats.total_score = int(total_score or 0)
    stats.streak_days = streak_days
    stats.last_submission = last_submission
    await db.flush()
    await delete_cache_keys("leaderboard")
    return stats


async def calculate_average_difficulty(db: AsyncSession, user_id: int) -> float:
    average = await db.scalar(
        select(func.coalesce(func.avg(PracticeProblem.difficulty), 0))
        .join(ProblemProgress, ProblemProgress.problem_id == PracticeProblem.id)
        .where(ProblemProgress.user_id == user_id, ProblemProgress.solved.is_(True))
    )
    return round(float(average or 0), 2)
