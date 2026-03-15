import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

API_URL = "https://codeforces.com/api/problemset.problems"
OUTPUT_FILE = "codeforces_1000_problems.json"
MIN_RATING = 800
MAX_RATING = 2000
MIN_PROBLEMS = 1000
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

ALLOWED_TOPICS = {
    "arrays",
    "strings",
    "math",
    "greedy",
    "dp",
    "graphs",
    "binary search",
    "two pointers",
    "sorting",
    "bit manipulation",
    "implementation",
}


def fetch_problemset(api_url: str) -> dict[str, Any]:
    try:
        with urlopen(api_url, timeout=30) as response:
            payload = response.read().decode("utf-8")
    except HTTPError as exc:
        raise RuntimeError(f"Codeforces API returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach Codeforces API: {exc.reason}") from exc

    data = json.loads(payload)
    if data.get("status") != "OK":
        raise RuntimeError(f"Codeforces API error: {data.get('comment', 'unknown error')}")
    return data["result"]



def normalize_tags(tags: list[str]) -> list[str]:
    return [tag.strip().lower() for tag in tags if tag and tag.strip()]



def map_topic(tags: list[str]) -> str:
    normalized = normalize_tags(tags)
    tag_set = set(normalized)

    for topic, candidates in TOPIC_PRIORITY:
        if tag_set & candidates:
            return topic

    if "implementation" in tag_set:
        return "implementation"
    if normalized:
        return "implementation"
    return "implementation"



def build_problem_id(contest_id: int, index: str) -> str:
    return f"{contest_id}{index}"



def build_link(contest_id: int, index: str) -> str:
    return f"https://codeforces.com/problemset/problem/{contest_id}/{index}"



def transform_problem(problem: dict[str, Any]) -> dict[str, Any] | None:
    contest_id = problem.get("contestId")
    index = problem.get("index")
    title = problem.get("name")
    rating = problem.get("rating")
    tags = normalize_tags(problem.get("tags", []))

    if contest_id is None or not index or not title or rating is None:
        return None
    if rating < MIN_RATING or rating > MAX_RATING:
        return None

    topic = map_topic(tags)
    if topic not in ALLOWED_TOPICS:
        return None

    return {
        "id": build_problem_id(contest_id, index),
        "title": title,
        "platform": PLATFORM,
        "difficulty": rating,
        "topic": topic,
        "tags": tags,
        "contestId": contest_id,
        "index": index,
        "link": build_link(contest_id, index),
    }



def deduplicate_problems(problems: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for problem in problems:
        problem_id = str(problem["id"])
        if problem_id in seen:
            continue
        seen.add(problem_id)
        unique.append(problem)
    return unique



def generate_dataset(api_url: str) -> list[dict[str, Any]]:
    result = fetch_problemset(api_url)
    raw_problems = result.get("problems", [])

    transformed = []
    for problem in raw_problems:
        item = transform_problem(problem)
        if item is not None:
            transformed.append(item)

    transformed = deduplicate_problems(transformed)
    transformed.sort(key=lambda item: (item["difficulty"], item["contestId"], item["index"]))

    if len(transformed) < MIN_PROBLEMS:
        raise RuntimeError(
            f"Filtered dataset contains only {len(transformed)} problems; expected at least {MIN_PROBLEMS}."
        )

    return transformed



def write_dataset(problems: list[dict[str, Any]], output_path: Path) -> None:
    payload = {"problems": problems}
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Codeforces practice dataset with 1000+ problems.",
    )
    parser.add_argument("--output", default=OUTPUT_FILE, help="Output JSON file path.")
    parser.add_argument("--api-url", default=API_URL, help="Codeforces API endpoint.")
    return parser.parse_args()



def main() -> int:
    args = parse_args()
    started = time.time()

    try:
        problems = generate_dataset(args.api_url)
        write_dataset(problems, Path(args.output))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    elapsed = time.time() - started
    print(f"Saved {len(problems)} problems to {args.output} in {elapsed:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
