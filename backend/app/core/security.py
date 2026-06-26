"""인증/인가 유틸리티.

역할:
- 비밀번호를 bcrypt 로 해싱/검증 (평문 저장 금지).
- JWT 액세스 토큰 발급/검증.
- FastAPI 의존성: 현재 로그인 사용자(get_current_user), 역할 제한(require_role).

초보자 메모:
- JWT 는 '서버가 서명한 출입증' 입니다. 로그인 성공 시 발급하고,
  이후 요청은 Authorization: Bearer <토큰> 헤더로 신원을 증명합니다.
- 서명 검증만으로 위조를 막으므로 서버는 토큰을 따로 저장할 필요가 없습니다(무상태).
"""
from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.domain import UserRole
from app.models import User

# tokenUrl 은 Swagger UI 의 'Authorize' 버튼이 토큰을 받아올 경로입니다.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login", auto_error=False
)


def hash_password(plain: str) -> str:
    """평문 비밀번호 → bcrypt 해시 문자열."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """평문 비밀번호가 저장된 해시와 일치하는지 검증."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user: User) -> str:
    """사용자 정보를 담은 JWT 액세스 토큰 발급."""
    now = datetime.now(UTC)
    payload = {
        "sub": str(user.id),          # 표준 클레임: 토큰 주체(사용자 id)
        "email": user.email,
        "role": user.role.value,
        "iat": now,
        "exp": now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """토큰 서명/만료 검증 후 payload 반환. 실패 시 401."""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Bearer 토큰 → 현재 사용자 객체. 인증 실패 시 401."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(token)
    user_id = payload.get("sub")
    user = db.get(User, int(user_id)) if user_id else None
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_role(*allowed: UserRole):
    """특정 역할만 통과시키는 의존성 팩토리.

    예) admin 전용: Depends(require_role(UserRole.admin))
    """

    def checker(current: Annotated[User, Depends(get_current_user)]) -> User:
        if current.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="권한이 없습니다.",
            )
        return current

    return checker


CurrentUser = Annotated[User, Depends(get_current_user)]
