from typing import Any

import httpx

from app.core.config import settings

LANGUAGE_MAP = {
    "cpp": 54,
    "c": 50,
    "java": 62,
    "python": 71,
}


def is_supported_language(language: str) -> bool:
    return language in LANGUAGE_MAP


async def submit_code(source_code: str, language: str, stdin: str, expected_output: str) -> dict[str, Any]:
    headers = {}
    if settings.judge0_api_key:
        headers["X-Auth-Token"] = settings.judge0_api_key

    payload = {
        "source_code": source_code,
        "language_id": LANGUAGE_MAP[language],
        "stdin": stdin,
        "expected_output": expected_output,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.judge0_url}/submissions?base64_encoded=false&wait=true",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
