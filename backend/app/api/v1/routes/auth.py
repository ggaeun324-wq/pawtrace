"""인증 라우트.

- POST /auth/register  회원가입(user 또는 shelter_staff)
- POST /auth/login     로그인 → JWT 발급
- GET  /auth/me        현재 로그인 사용자 정보
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import CurrentUser
from app.db.session import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.services import auth_service

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: RegisterRequest, db: Annotated[Session, Depends(get_db)]):
    return auth_service.register(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    user = auth_service.authenticate(db, data.email, data.password)
    return TokenResponse(access_token=auth_service.issue_token(user))


@router.get("/me", response_model=UserOut)
def me(current: CurrentUser):
    return current
