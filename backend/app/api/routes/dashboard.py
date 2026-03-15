from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.practice import ProblemProgress, PracticeProblem
from app.models.quiz import CodingQuestion, MCQQuestion, QuestionType, Submission, SubmissionStatus
from app.models.user import User
from app.services.cache import cache_json, get_cached_json
from app.services.deps import get_current_user

router = APIRouter()


@router.get("/stats")
async def student_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    cache_key = f"dashboard:student:{current_user.id}"
    cached = await get_cached_json(cache_key)
    if cached:
        return cached

    solved_count = await db.scalar(
        select(func.count()).select_from(ProblemProgress).where(
            ProblemProgress.user_id == current_user.id,
            ProblemProgress.solved.is_(True),
        )
    )

    quiz_score = await db.scalar(
        select(func.coalesce(func.avg(Submission.score), 0)).where(
            Submission.user_id == current_user.id,
            Submission.quiz_id.is_not(None),
        )
    )

    mcq_topic_scores = (
        await db.execute(
            select(MCQQuestion.topic, func.avg(Submission.score))
            .join(MCQQuestion, Submission.mcq_question_id == MCQQuestion.id)
            .where(
                Submission.user_id == current_user.id,
                Submission.question_type == QuestionType.mcq,
            )
            .group_by(MCQQuestion.topic)
        )
    ).all()
    coding_topic_scores = (
        await db.execute(
            select(CodingQuestion.topic, func.avg(Submission.score))
            .join(CodingQuestion, Submission.coding_question_id == CodingQuestion.id)
            .where(
                Submission.user_id == current_user.id,
                Submission.question_type == QuestionType.coding,
            )
            .group_by(CodingQuestion.topic)
        )
    ).all()

    topic_scores: dict[str, list[float]] = {}
    for topic, score in [*mcq_topic_scores, *coding_topic_scores]:
        topic_scores.setdefault(topic, []).append(float(score or 0))

    weak_topics = [
        topic
        for topic, scores in sorted(
            topic_scores.items(),
            key=lambda item: sum(item[1]) / len(item[1]),
        )[:5]
    ]

    if not weak_topics:
        weak_topics = ["graphs", "dynamic-programming"]

    activity_rows = (
        await db.execute(
            select(func.date(Submission.created_at), func.count(Submission.id))
            .where(Submission.user_id == current_user.id)
            .group_by(func.date(Submission.created_at))
            .order_by(func.date(Submission.created_at).desc())
            .limit(30)
        )
    ).all()
    activity_heatmap = [
        {"date": str(activity_date), "count": submission_count}
        for activity_date, submission_count in reversed(activity_rows)
    ]

    payload = {
        "solved_problems": solved_count or 0,
        "quiz_score": round(float(quiz_score or 0), 2),
        "weak_topics": weak_topics,
        "activity_heatmap": activity_heatmap,
    }
    await cache_json(cache_key, payload, ttl=120)
    return payload
