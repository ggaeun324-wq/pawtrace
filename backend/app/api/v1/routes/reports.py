"""신고 접수 라우트.

- POST /reports   의심 사례(검증 필요) 신고 접수
MVP는 접수만 하고, 관리자 검토/신뢰도 반영은 admin 기능(P1 후반)에서 처리합니다.
"""
from fastapi import APIRouter

from app.schemas.report import ReportCreate, ReportCreated

router = APIRouter()

# TODO: DB 저장으로 교체. 현재는 접수 확인만 반환.
_NEXT_ID = {"value": 1}


@router.post("", response_model=ReportCreated, status_code=201)
def create_report(payload: ReportCreate):
    report_id = _NEXT_ID["value"]
    _NEXT_ID["value"] += 1
    return ReportCreated(id=report_id)
