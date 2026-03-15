import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select, tuple_  # noqa: E402

from app.db.session import SessionLocal  # noqa: E402
from app.models.practice import PracticeProblem  # noqa: E402

DEFAULT_INPUT = "codeforces_1000_problems.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import Codeforces practice problems into PostgreSQL.")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Path to codeforces dataset JSON file.")
    return parser.parse_args()


def load_problems(input_path: Path) -> list[dict]:
    if not input_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {input_path}")

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    problems = payload.get("problems")
    if not isinstance(problems, list):
        raise ValueError("Invalid dataset format: expected top-level 'problems' list")
    return problems


async def import_problems(problems: list[dict]) -> int:
    inserted = 0

    keys = [
        (problem.get("contestId"), problem.get("index"))
        for problem in problems
        if problem.get("contestId") is not None and problem.get("index")
    ]

    async with SessionLocal() as session:
        existing_keys: set[tuple[int, str]] = set()
        if keys:
            result = await session.execute(
                select(PracticeProblem.contest_id, PracticeProblem.problem_index).where(
                    tuple_(PracticeProblem.contest_id, PracticeProblem.problem_index).in_(keys)
                )
            )
            existing_keys = {(contest_id, problem_index) for contest_id, problem_index in result.all()}

        for item in problems:
            contest_id = item.get("contestId")
            problem_index = item.get("index")
            if contest_id is None or not problem_index:
                continue
            if (contest_id, problem_index) in existing_keys:
                continue

            session.add(
                PracticeProblem(
                    title=item.get("title", ""),
                    platform=item.get("platform", "Codeforces"),
                    difficulty=int(item.get("difficulty", 0)),
                    topic=item.get("topic", "implementation"),
                    tags=item.get("tags", []),
                    contest_id=contest_id,
                    problem_index=problem_index,
                    link=item.get("link", ""),
                )
            )
            existing_keys.add((contest_id, problem_index))
            inserted += 1

        await session.commit()

    return inserted


async def async_main() -> int:
    args = parse_args()
    input_path = (ROOT / args.input).resolve() if not Path(args.input).is_absolute() else Path(args.input)

    try:
        problems = load_problems(input_path)
        inserted = await import_problems(problems)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Inserted {inserted} problems.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(async_main()))
