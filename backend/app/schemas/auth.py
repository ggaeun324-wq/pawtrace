"""인증/회원 응답·요청 스키마.

회원가입은 두 종류를 지원합니다.
- 일반 사용자(user)
- 보호소 직원(shelter_staff): shelter_id 필요(담당 보호소)
플랫폼 관리자(admin)는 자가가입 불가 — 시드/내부 승격으로만 생성합니다.
"""
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)  # bcrypt 72바이트 한도
    display_name: str = Field(min_length=1, max_length=60)
    # 가입 시 선택 가능한 역할은 user / shelter_staff 뿐(admin 제외).
    role: UserRole = UserRole.user
    shelter_id: int | None = None  # shelter_staff 인 경우 담당 보호소


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    display_name: str
    role: UserRole
    shelter_id: int | None = None
