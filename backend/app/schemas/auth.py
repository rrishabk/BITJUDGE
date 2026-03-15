from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.config import settings
from app.models.user import UserRole

ADMIN_EMAIL = "admin@juetguna.in"


class UserCreate(BaseModel):
    name: str
    enrollment_number: str
    email: EmailStr
    password: str = Field(min_length=8)
    codeforces_handle: str | None = None
    codechef_handle: str | None = None
    leetcode_handle: str | None = None
    hackerrank_handle: str | None = None
    github_handle: str | None = None

    @field_validator("email")
    @classmethod
    def validate_domain(cls, value: EmailStr) -> str:
        normalized = str(value).lower()
        if normalized != ADMIN_EMAIL and not normalized.endswith(f"@{settings.allowed_email_domain}"):
            raise ValueError("Only JUET students can login.")
        return normalized


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        normalized = str(value).lower()
        if normalized != ADMIN_EMAIL and not normalized.endswith(f"@{settings.allowed_email_domain}"):
            raise ValueError("Only JUET students can login.")
        return normalized


class UserOut(BaseModel):
    id: int
    name: str
    enrollment_number: str
    email: EmailStr
    role: UserRole
    codeforces_handle: str | None
    codechef_handle: str | None
    leetcode_handle: str | None
    hackerrank_handle: str | None
    github_handle: str | None

    model_config = {"from_attributes": True}


class LoginUserOut(BaseModel):
    name: str
    role: UserRole

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    token: str
    user: LoginUserOut
