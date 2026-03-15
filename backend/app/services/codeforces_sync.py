from __future__ import annotations

from typing import Any

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, tuple_

from app.db.session import SessionLocal
from app.models.practice import PracticeProblem
from app.services.cache import delete_cache_keys, delete_cache_prefix

CODEFORCES_API_URL = "https://codeforces.com/api/problemset.problems"
MIN_RATING = 800
MAX_RATING = 2000
SYNC_INTERVAL_HOURS = 24
PLATFORM = "Codeforces"

TOPIC_PRIORITY = [
    ("dp", {"dp"}),
    ("graphs", {"graphs", "graph matchings", "dfs and similar", "shortest paths", "trees"}),
    ("binary search", {"binary search", "ternary search"}),
    ("two pointers", {"two pointers", "meet-in-the-middle", "sliding window"}),
    ("bit manipulation", {"bitmasks"}),
    ("greedy", {"greedy"}),
    ("sorting", {"sortings"}),
    ("strings", {"strings", "string suffix structures", "expression parsing"}),
    ("arrays", {"data structures", "constructive algorithms", "brute force", "hashing", "matrices"}),
    ("math", {"math", "number theory", "combinatorics", "probabilities", "games"}),
    ("implementation", {"implementation"}),
]

scheduler: AsyncIOScheduler | None = None


async def fetch_problemset() -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(CODEFORCES_API_URL)
        response.raise_for_status()
        payload = response.json()

    if payload.get("status") != "OK":
        raise RuntimeError(payload.get("comment", "Codeforces API request failed"))
    return payload["result"].get("problems", [])



def normalize_tags(tags: list[str]) -> list[str]:
    return [tag.strip().lower() for tag in tags if tag and tag.strip()]



def map_topic(tags: list[str]) -> str:
    tag_set = set(normalize_tags(tags))
    for topic, candidates in TOPIC_PRIORITY:
        if tag_set & candidates:
            return topic
    return "implementation"



def transform_problem(problem: dict[str, Any]) -> dict[str, Any] | None:
    contest_id = problem.get("contestId")
    problem_index = problem.get("index")
    title = problem.get("name")
    rating = problem.get("rating")
    tags = normalize_tags(problem.get("tags", []))

    if contest_id is None or not problem_index or not title or rating is None:
        return None
    if rating < MIN_RATING or rating > MAX_RATING:
        return None

    return {
        "title": title,
        "platform": PLATFORM,
        "difficulty": int(rating),
        "topic": map_topic(tags),
        "tags": tags,
        "contest_id": int(contest_id),
        "problem_index": str(problem_index),
        "link": f"https://codeforces.com/problemset/problem/{contest_id}/{problem_index}",
    }


async def sync_codeforces_problems() -> int:
    raw_problems = await fetch_problemset()
    transformed = [item for item in (transform_problem(problem) for problem in raw_problems) if item is not None]
    keys = [(item["contest_id"], item["problem_index"]) for item in transformed]

    inserted = 0
    async with SessionLocal() as session:
        existing_keys: set[tuple[int, str]] = set()
        if keys:
            result = await session.execute(
                select(PracticeProblem.contest_id, PracticeProblem.problem_index).where(
                    tuple_(PracticeProblem.contest_id, PracticeProblem.problem_index).in_(keys)
                )
            )
            existing_keys = {(contest_id, problem_index) for contest_id, problem_index in result.all()}

        for item in transformed:
            key = (item["contest_id"], item["problem_index"])
            if key in existing_keys:
                continue
            session.add(PracticeProblem(**item))
            existing_keys.add(key)
            inserted += 1

        await session.commit()

    if inserted > 0:
        await delete_cache_keys("dashboard:admin:stats")
        await delete_cache_prefix("practice:")
    return inserted


async def trigger_problem_sync() -> None:
    await sync_codeforces_problems()


def start_codeforces_scheduler() -> AsyncIOScheduler:
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(sync_codeforces_problems, "interval", hours=SYNC_INTERVAL_HOURS, id="codeforces-sync", replace_existing=True)
        scheduler.start()
    return scheduler


async def stop_codeforces_scheduler() -> None:
    global scheduler
    if scheduler is not None:
        scheduler.shutdown(wait=False)
        scheduler = None
