"""인증 서비스 (회원가입/로그인 비즈니스 규칙)."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.domain import UserRole
from app.models import Shelter, User
from app.repositories import user_repository
from app.schemas.auth import RegisterRequest


def register(db: Session, data: RegisterRequest) -> User:
    """신규 회원 생성.

    규칙:
    - 이메일 중복 불가.
    - admin 역할은 자가가입 금지(403).
    - shelter_staff 는 존재하는 shelter_id 필요.
    """
    if data.role == UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 계정은 직접 가입할 수 없습니다.",
        )

    if user_repository.get_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가입된 이메일입니다.",
        )

    shelter_id = None
    if data.role == UserRole.shelter_staff:
        if data.shelter_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="보호소 직원은 담당 보호소(shelter_id)가 필요합니다.",
            )
        if db.get(Shelter, data.shelter_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 보호소를 찾을 수 없습니다.",
            )
        shelter_id = data.shelter_id

    return user_repository.create(
        db,
        email=data.email,
        hashed_password=hash_password(data.password),
        display_name=data.display_name,
        role=data.role,
        shelter_id=shelter_id,
    )


def authenticate(db: Session, email: str, password: str) -> User:
    """이메일+비밀번호 검증. 실패 시 401(존재/비번 구분 노출 안 함)."""
    user = user_repository.get_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )
    return user


def issue_token(user: User) -> str:
    return create_access_token(user)
