from app.api.routes.quiz import _map_judge0_status
from app.models.quiz import SubmissionStatus
from app.schemas.quiz import CodingQuestionCreate, SubmissionCreate


def test_judge0_status_mapping() -> None:
    assert _map_judge0_status("Accepted") == (SubmissionStatus.accepted, 100)
    assert _map_judge0_status("Compilation Error") == (SubmissionStatus.compilation_error, 0)
    assert _map_judge0_status("Runtime Error (NZEC)") == (SubmissionStatus.runtime_error, 0)
    assert _map_judge0_status("Wrong Answer") == (SubmissionStatus.wrong_answer, 0)


def test_mcq_submission_validation() -> None:
    payload = SubmissionCreate(question_type="mcq", mcq_question_id=1, selected_option="A")
    assert payload.mcq_question_id == 1


def test_coding_submission_validation_and_language_normalization() -> None:
    payload = SubmissionCreate(
        question_type="coding",
        coding_question_id=2,
        source_code="print(1)",
        language="Python",
    )
    assert payload.language == "python"


def test_coding_question_language_normalization() -> None:
    payload = CodingQuestionCreate(
        question="Solve",
        sample_input="1",
        sample_output="1",
        testcases=[{"input": "1", "output": "1"}],
        languages=["C++", "Java", "Python"],
        topic="graphs",
    )
    assert payload.languages == ["cpp", "java", "python"]
