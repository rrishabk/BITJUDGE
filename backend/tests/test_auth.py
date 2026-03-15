from fastapi import HTTPException, status

from app.core.security import create_access_token, decode_token, get_password_hash, verify_password
from app.models.user import User, UserRole
from app.schemas.auth import UserCreate, UserLogin
from app.services.deps import check_admin_role


def test_password_hashing_round_trip() -> None:
    password = "StrongPass123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_email_domain_validation_enforces_juet_domain() -> None:
    payload = UserLogin(email="student@juetguna.in", password="StrongPass123")
    assert str(payload.email) == "student@juetguna.in"

    try:
        UserLogin(email="student@example.com", password="StrongPass123")
    except Exception as exc:
        assert "Only JUET students can login." in str(exc)
    else:
        raise AssertionError("Invalid domain should fail validation")


def test_default_admin_email_is_allowed() -> None:
    payload = UserLogin(email="admin@juetguna.in", password="admin@8279ViJio")
    assert str(payload.email) == "admin@juetguna.in"


def test_admin_create_schema_keeps_same_domain_rule() -> None:
    payload = UserCreate(
        name="Student",
        enrollment_number="EN001",
        email="student@juetguna.in",
        password="StrongPass123",
    )
    assert str(payload.email) == "student@juetguna.in"


def test_jwt_contains_user_identity_and_role() -> None:
    token = create_access_token(subject="admin@juetguna.in", user_id=7, role="admin")
    payload = decode_token(token)
    assert payload["sub"] == "admin@juetguna.in"
    assert payload["uid"] == 7
    assert payload["role"] == "admin"


def test_admin_role_check_allows_admin_only() -> None:
    admin_user = User(
        id=1,
        name="Admin",
        enrollment_number="AD001",
        email="admin@juetguna.in",
        password_hash="hashed",
        role=UserRole.admin,
    )
    assert check_admin_role(admin_user) is admin_user

    student_user = User(
        id=2,
        name="Student",
        enrollment_number="ST001",
        email="student@juetguna.in",
        password_hash="hashed",
        role=UserRole.student,
    )
    try:
        check_admin_role(student_user)
    except HTTPException as exc:
        assert exc.status_code == status.HTTP_403_FORBIDDEN
    else:
        raise AssertionError("Student should not pass admin middleware")
