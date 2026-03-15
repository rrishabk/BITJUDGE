from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User, UserStats
from app.schemas.leaderboard import LeaderboardEntry
from app.services.cache import cache_json, get_cached_json
from app.services.deps import get_current_user

router = APIRouter()


@router.get("", response_model=list[LeaderboardEntry])
async def get_leaderboard(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[LeaderboardEntry]:
    cached = await get_cached_json("leaderboard")
    if cached:
        return [LeaderboardEntry(**item) for item in cached]

    rows = (
        await db.execute(
            select(User.name, UserStats.problems_solved, UserStats.total_score)
            .join(UserStats, UserStats.user_id == User.id)
            .order_by(UserStats.total_score.desc(), UserStats.problems_solved.desc(), User.name.asc())
            .limit(100)
        )
    ).all()

    payload = [
        LeaderboardEntry(
            rank=index,
            name=name,
            problems_solved=int(problems_solved or 0),
            score=int(total_score or 0),
        )
        for index, (name, problems_solved, total_score) in enumerate(rows, start=1)
    ]
    await cache_json("leaderboard", [item.model_dump() for item in payload], ttl=120)
    return payload
