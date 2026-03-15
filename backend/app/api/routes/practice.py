from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.practice import PracticeProblem, ProblemProgress
from app.models.user import User
from app.schemas.practice import PracticeProblemOut, ProblemProgressResponse, ProblemProgressUpdate
from app.services.cache import cache_json, delete_cache_keys, delete_cache_prefix, get_cached_json
from app.services.deps import get_current_user

router = APIRouter()


async def _get_progress_map(current_user: User, db: AsyncSession) -> dict[int, bool]:
    progress_rows = (
        await db.execute(select(ProblemProgress).where(ProblemProgress.user_id == current_user.id))
    ).scalars().all()
    return {row.problem_id: row.solved for row in progress_rows}


async def _serialize_problems(
    problems: list[PracticeProblem],
    current_user: User,
    db: AsyncSession,
) -> list[PracticeProblemOut]:
    solved_map = await _get_progress_map(current_user, db)
    return [
        PracticeProblemOut(
            id=problem.id,
            title=problem.title,
            platform=problem.platform,
            link=problem.link,
            difficulty=problem.difficulty,
            topic=problem.topic,
            solved=solved_map.get(problem.id, False),
        )
        for problem in problems
    ]


@router.get("", response_model=list[PracticeProblemOut])
async def list_problems(
    topic: str | None = None,
    difficulty: int | None = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=settings.page_size_default, ge=1, le=settings.page_size_max),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PracticeProblemOut]:
    cache_key = f"problems:{current_user.id}:{topic or 'all'}:{difficulty or 'all'}:{page}:{limit}"
    cached = await get_cached_json(cache_key)
    if cached:
        return [PracticeProblemOut(**item) for item in cached]

    query = select(PracticeProblem)
    if topic:
        query = query.where(PracticeProblem.topic == topic)
    if difficulty is not None:
        query = query.where(PracticeProblem.difficulty == difficulty)

    problems = (
        await db.execute(
            query.order_by(PracticeProblem.difficulty.asc(), PracticeProblem.id.asc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
    ).scalars().all()
    payload = await _serialize_problems(problems, current_user, db)
    await cache_json(cache_key, [item.model_dump() for item in payload], ttl=180)
    return payload


@router.get("/{problem_id}", response_model=PracticeProblemOut)
async def get_problem(
    problem_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PracticeProblemOut:
    problem = await db.get(PracticeProblem, problem_id)
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

    solved_map = await _get_progress_map(current_user, db)
    return PracticeProblemOut(
        id=problem.id,
        title=problem.title,
        platform=problem.platform,
        link=problem.link,
        difficulty=problem.difficulty,
        topic=problem.topic,
        solved=solved_map.get(problem.id, False),
    )


@router.post("/mark-solved", response_model=ProblemProgressResponse, status_code=status.HTTP_200_OK)
async def mark_problem_solved(
    payload: ProblemProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProblemProgressResponse:
    problem = await db.get(PracticeProblem, payload.problem_id)
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

    result = await db.execute(
        select(ProblemProgress).where(
            ProblemProgress.user_id == current_user.id,
            ProblemProgress.problem_id == payload.problem_id,
        )
    )
    progress = result.scalar_one_or_none()
    if progress is None:
        progress = ProblemProgress(user_id=current_user.id, problem_id=payload.problem_id, solved=payload.solved)
        db.add(progress)
    else:
        progress.solved = payload.solved
        progress.solved_at = func.now() if payload.solved else None
    if progress.solved and progress.solved_at is None:
        progress.solved_at = func.now()

    await db.commit()

    total_solved = await db.scalar(
        select(func.count()).select_from(ProblemProgress).where(
            ProblemProgress.user_id == current_user.id,
            ProblemProgress.solved.is_(True),
        )
    )
    total_problems = await db.scalar(select(func.count()).select_from(PracticeProblem))

    await delete_cache_keys(f"dashboard:student:{current_user.id}")
    await delete_cache_prefix(f"problems:{current_user.id}:")

    return ProblemProgressResponse(
        problem_id=payload.problem_id,
        solved=payload.solved,
        total_solved=int(total_solved or 0),
        remaining_problems=max(int(total_problems or 0) - int(total_solved or 0), 0),
    )
