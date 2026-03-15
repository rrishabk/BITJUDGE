from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.quiz import CodingQuestion, MCQQuestion, QuestionType, Quiz, Submission, SubmissionStatus
from app.models.user import User
from app.schemas.quiz import QuizOut, SubmissionCreate, SubmissionOut
from app.services.cache import delete_cache_keys
from app.services.deps import get_current_user
from app.services.judge0 import is_supported_language, submit_code

router = APIRouter()


def _map_judge0_status(description: str) -> tuple[SubmissionStatus, int]:
    normalized = description.lower()
    if normalized == "accepted":
        return SubmissionStatus.accepted, 100
    if "compile" in normalized:
        return SubmissionStatus.compilation_error, 0
    if "runtime" in normalized:
        return SubmissionStatus.runtime_error, 0
    return SubmissionStatus.wrong_answer, 0


def _submission_response(submission: Submission) -> SubmissionOut:
    return SubmissionOut(
        id=submission.id,
        question_type=submission.question_type,
        verdict=submission.status.value,
        status=submission.status,
        score=submission.score,
        execution_time=submission.execution_time,
        memory_used=submission.memory_used,
        verdict_payload=submission.verdict_payload,
    )


@router.get("/active", response_model=list[QuizOut])
async def active_quizzes(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[QuizOut]:
    now = datetime.now(timezone.utc)
    quizzes = (
        await db.execute(
            select(Quiz)
            .where(Quiz.is_published.is_(True), Quiz.start_time <= now, Quiz.end_time >= now)
            .order_by(Quiz.start_time.asc())
        )
    ).scalars().all()
    return [QuizOut.model_validate(quiz) for quiz in quizzes]


@router.get("/previous", response_model=list[QuizOut])
async def previous_quizzes(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[QuizOut]:
    now = datetime.now(timezone.utc)
    quizzes = (
        await db.execute(
            select(Quiz)
            .where(Quiz.is_published.is_(True), Quiz.end_time < now)
            .order_by(Quiz.end_time.desc())
        )
    ).scalars().all()
    return [QuizOut.model_validate(quiz) for quiz in quizzes]


@router.post("/submit", response_model=SubmissionOut, status_code=status.HTTP_201_CREATED)
async def submit_solution(
    payload: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionOut:
    submission = Submission(
        user_id=current_user.id,
        quiz_id=payload.quiz_id,
        question_type=payload.question_type,
        mcq_question_id=payload.mcq_question_id,
        coding_question_id=payload.coding_question_id,
        source_code=payload.source_code,
        selected_option=payload.selected_option,
        language=payload.language,
        status=SubmissionStatus.pending,
        score=0,
    )

    if payload.question_type == QuestionType.mcq:
        mcq_question = await db.get(MCQQuestion, payload.mcq_question_id)
        if mcq_question is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCQ question not found")
        submission.status = (
            SubmissionStatus.accepted if payload.selected_option == mcq_question.correct_answer else SubmissionStatus.wrong_answer
        )
        submission.score = 100 if submission.status == SubmissionStatus.accepted else 0
        submission.verdict_payload = {
            "correct_answer": mcq_question.correct_answer,
            "selected_option": payload.selected_option,
            "verdict": submission.status.value,
        }
    else:
        coding_question = await db.get(CodingQuestion, payload.coding_question_id)
        if coding_question is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coding question not found")
        if not payload.language or not is_supported_language(payload.language):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported language")
        if payload.language not in coding_question.languages:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Language not allowed for this question")

        submission.status = SubmissionStatus.running
        first_case = coding_question.testcases[0]
        result = await submit_code(
            source_code=payload.source_code or "",
            language=payload.language,
            stdin=first_case["input"],
            expected_output=first_case["output"],
        )
        description = result.get("status", {}).get("description", "")
        submission.judge0_token = result.get("token")
        submission.execution_time = result.get("time")
        submission.memory_used = result.get("memory")
        submission.verdict_payload = result
        submission.status, submission.score = _map_judge0_status(description)

    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    await delete_cache_keys(
        f"dashboard:student:{current_user.id}",
        "dashboard:admin:stats",
    )
    return _submission_response(submission)
