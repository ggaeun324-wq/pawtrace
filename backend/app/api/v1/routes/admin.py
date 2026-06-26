"""관리자 라우트 (admin 전용).

- POST /admin/sync/public-data  공공데이터(유기동물)를 가져와 DB 에 멱등 반영.

권한: require_role(admin) 의존성으로 admin 토큰만 통과합니다.
공공데이터 키가 없으면 동기화는 0건으로 끝나며, 키 설정 안내 메시지를 반환합니다.
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import require_role
from app.db.session import get_db
from app.domain import UserRole
from app.models import User
from app.schemas.admin import SyncResult
from app.services import sync_service

router = APIRouter()


@router.post("/sync/public-data", response_model=SyncResult)
def sync_public_data(
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[User, Depends(require_role(UserRole.admin))],
    begin: str | None = None,  # 'YYYYMMDD' 발견일 시작(선택)
    end: str | None = None,    # 'YYYYMMDD' 발견일 종료(선택)
    rows: int = 50,
    page: int = 1,
):
    result = sync_service.sync_public_data(db, begin=begin, end=end, rows=rows, page=page)
    if result["source_enabled"]:
        msg = f"공공데이터 동기화 완료: 강아지 {result['dogs_total']}건 반영."
    else:
        msg = (
            "PUBLIC_DATA_API_KEY 가 설정되지 않아 실제 동기화는 건너뛰었습니다. "
            "data.go.kr 에서 키를 발급해 환경변수로 주입하면 실데이터가 반영됩니다."
        )
    result["message"] = msg
    return result
