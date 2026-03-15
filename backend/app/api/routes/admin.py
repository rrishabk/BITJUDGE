import csv
import re
import secrets
import string
from io import StringIO

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.practice import PracticeProblem
from app.models.quiz import CodingQuestion, MCQQuestion, Quiz, QuizQuestionLink, Submission
from app.models.user import User, UserRole, UserStats
from app.schemas.auth import UserCreate
from app.schemas.quiz import CodingQuestionCreate, MCQCreate, QuizCreate, QuizOut, QuizQuestionAttach
from app.services.cache import cache_json, delete_cache_keys, get_cached_json
from app.services.codeforces_sync import trigger_problem_sync
from app.services.deps import require_admin
from app.services.stats import ensure_user_stats

router = APIRouter()


def _generate_random_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _normalize_csv_email(raw_email: str) -> str:
    email = raw_email.strip()
    mailto_match = re.search(r"mailto:([^\)\]]+)", email, flags=re.IGNORECASE)
    if mailto_match:
        email = mailto_match.group(1).strip()
    email = re.sub(r"^[\[]", "", email)
    email = re.sub(r"[\]].*$", "", email)
    return email.lower()


def _validate_juet_email(email: str) -> str:
    normalized = _normalize_csv_email(email)
    if not normalized.endswith(f"@{settings.allowed_email_domain}"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only JUET students can login.")
    return normalized


@router.post("/create-user", status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict[str, str]:
    existing = await db.execute(
        select(User).where(
            or_(
                User.email == str(payload.email),
                User.enrollment_number == payload.enrollment_number,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or enrollment number already registered",
        )

    user = User(
        name=payload.name,
        email=str(payload.email),
        enrollment_number=payload.enrollment_number,
        password_hash=get_password_hash(payload.password),
        role=UserRole.student,
        codeforces_handle=payload.codeforces_handle,
        codechef_handle=payload.codechef_handle,
        leetcode_handle=payload.leetcode_handle,
        hackerrank_handle=payload.hackerrank_handle,
        github_handle=payload.github_handle,
    )
    db.add(user)
    await db.flush()
    await ensure_user_stats(db, user.id)
    await db.commit()
    await delete_cache_keys("leaderboard", "dashboard:admin:stats")
    return {"message": "User created successfully"}


@router.post("/import-users", status_code=status.HTTP_201_CREATED)
async def import_users(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Upload a valid CSV file")

    content = await file.read()
    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV file must be UTF-8 encoded") from exc

    reader = csv.DictReader(StringIO(decoded))
    required_columns = {"name", "email", "enrollment_number"}
    if reader.fieldnames is None or not required_columns.issubset({field.strip() for field in reader.fieldnames}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV must contain name,email,enrollment_number columns",
        )

    rows = list(reader)
    if not rows:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV file is empty")

    created_users: list[dict[str, str]] = []
    seen_pairs: set[tuple[str, str]] = set()

    for row in rows:
        name = (row.get("name") or "").strip()
        raw_email = row.get("email") or ""
        enrollment_number = (row.get("enrollment_number") or "").strip()

        if not name or not raw_email or not enrollment_number:
            continue

        email = _validate_juet_email(raw_email)
        pair = (email, enrollment_number)
        if pair in seen_pairs:
            continue

        existing = await db.execute(
            select(User).where(
                or_(
                    User.email == email,
                    User.enrollment_number == enrollment_number,
                )
            )
        )
        if existing.scalar_one_or_none():
            continue

        generated_password = _generate_random_password()
        user = User(
            name=name,
            email=email,
            enrollment_number=enrollment_number,
            password_hash=get_password_hash(generated_password),
            role=UserRole.student,
        )
        db.add(user)
        await db.flush()
        await ensure_user_stats(db, user.id)
        seen_pairs.add(pair)
        created_users.append(
            {
                "name": name,
                "email": email,
                "enrollment_number": enrollment_number,
                "password": generated_password,
            }
        )

    await db.commit()
    await delete_cache_keys("leaderboard", "dashboard:admin:stats")
    return {
        "created_count": len(created_users),
        "created_users": created_users,
    }


@router.get("/users")
async def list_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[dict]:
    users = (
        await db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
    ).scalars().all()
    return [
        {
            "id": user.id,
            "name": user.name,
            "enrollment_number": user.enrollment_number,
            "email": user.email,
            "role": user.role.value,
            "created_at": user.created_at,
        }
        for user in users
    ]


@router.get("/quizzes", response_model=list[QuizOut])
async def list_quizzes(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[QuizOut]:
    quizzes = (
        await db.execute(
            select(Quiz)
            .order_by(Quiz.start_time.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
    ).scalars().all()
    return [QuizOut.model_validate(quiz) for quiz in quizzes]


@router.get("/problems")
async def list_problems(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[dict]:
    problems = (
        await db.execute(
            select(PracticeProblem)
            .order_by(PracticeProblem.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
    ).scalars().all()
    return [
        {
            "id": problem.id,
            "title": problem.title,
            "platform": problem.platform,
            "difficulty": problem.difficulty,
            "topic": problem.topic,
            "contest_id": problem.contest_id,
            "problem_index": problem.problem_index,
            "link": problem.link,
        }
        for problem in problems
    ]


@router.get("/questions")
async def list_questions(
    question_type: str | None = Query(default=None, pattern="^(mcq|coding)?$"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    response: dict[str, list[dict]] = {"mcq": [], "coding": []}

    if question_type in {None, "mcq"}:
        mcqs = (
            await db.execute(
                select(MCQQuestion)
                .order_by(MCQQuestion.created_at.desc())
                .offset((page - 1) * limit)
                .limit(limit)
            )
        ).scalars().all()
        response["mcq"] = [
            {
                "id": question.id,
                "question": question.question,
                "topic": question.topic,
                "options": question.options,
                "correct_answer": question.correct_answer,
            }
            for question in mcqs
        ]

    if question_type in {None, "coding"}:
        coding_questions = (
            await db.execute(
                select(CodingQuestion)
                .order_by(CodingQuestion.created_at.desc())
                .offset((page - 1) * limit)
                .limit(limit)
            )
        ).scalars().all()
        response["coding"] = [
            {
                "id": question.id,
                "question": question.question,
                "topic": question.topic,
                "languages": question.languages,
                "sample_input": question.sample_input,
                "sample_output": question.sample_output,
            }
            for question in coding_questions
        ]

    return response


@router.post("/create-quiz", response_model=QuizOut, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    payload: QuizCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> QuizOut:
    quiz = Quiz(**payload.model_dump())
    db.add(quiz)
    await db.commit()
    await db.refresh(quiz)
    await delete_cache_keys("dashboard:admin:stats")
    return QuizOut.model_validate(quiz)


@router.post("/add-mcq", status_code=status.HTTP_201_CREATED)
async def add_mcq(
    payload: MCQCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> MCQQuestion:
    if payload.correct_answer not in payload.options:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Correct answer must be one of the options")
    mcq = MCQQuestion(**payload.model_dump())
    db.add(mcq)
    await db.commit()
    await db.refresh(mcq)
    await delete_cache_keys("dashboard:admin:stats")
    return mcq


@router.post("/add-coding-question", status_code=status.HTTP_201_CREATED)
async def add_coding_question(
    payload: CodingQuestionCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> CodingQuestion:
    coding_question = CodingQuestion(**payload.model_dump())
    db.add(coding_question)
    await db.commit()
    await db.refresh(coding_question)
    await delete_cache_keys("dashboard:admin:stats")
    return coding_question


@router.post("/add-question", status_code=status.HTTP_201_CREATED)
async def add_question(
    payload: QuizQuestionAttach,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> QuizQuestionLink:
    quiz = await db.get(Quiz, payload.quiz_id)
    if quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    if payload.question_type.value == "mcq":
        question = await db.get(MCQQuestion, payload.question_id)
    else:
        question = await db.get(CodingQuestion, payload.question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    link = QuizQuestionLink(**payload.model_dump())
    db.add(link)
    await db.commit()
    await db.refresh(link)
    await delete_cache_keys("dashboard:admin:stats")
    return link


@router.post("/sync-problems", status_code=status.HTTP_202_ACCEPTED)
async def sync_problems(
    background_tasks: BackgroundTasks,
    _: User = Depends(require_admin),
) -> dict[str, str]:
    background_tasks.add_task(trigger_problem_sync)
    return {"status": "accepted", "message": "Codeforces sync started"}


@router.get("/stats")
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    cached = await get_cached_json("dashboard:admin:stats")
    if cached:
        return cached

    total_users = await db.scalar(select(func.count()).select_from(User))
    total_quizzes = await db.scalar(select(func.count()).select_from(Quiz))
    total_submissions = await db.scalar(select(func.count()).select_from(Submission))
    top_user_rows = (
        await db.execute(
            select(
                User.id,
                User.name,
                User.enrollment_number,
                func.coalesce(UserStats.total_score, 0).label("score"),
                func.coalesce(UserStats.problems_solved, 0).label("problems_solved"),
            )
            .outerjoin(UserStats, UserStats.user_id == User.id)
            .order_by(
                func.coalesce(UserStats.total_score, 0).desc(),
                func.coalesce(UserStats.problems_solved, 0).desc(),
                User.name.asc(),
            )
            .limit(10)
        )
    ).all()

    payload = {
        "total_users": int(total_users or 0),
        "total_quizzes": int(total_quizzes or 0),
        "total_submissions": int(total_submissions or 0),
        "top_users": [
            {
                "user_id": user_id,
                "name": name,
                "enrollment_number": enrollment_number,
                "score": int(score or 0),
                "problems_solved": int(problems_solved or 0),
            }
            for user_id, name, enrollment_number, score, problems_solved in top_user_rows
        ],
    }
    await cache_json("dashboard:admin:stats", payload, ttl=120)
    return payload
