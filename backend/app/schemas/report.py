"""신고 접수 스키마.

표현 원칙: '불법/펫샵 확정' 같은 단정 금지.
사용자는 '검증 필요' 사례를 사실 위주로 신고합니다.
"""
from pydantic import BaseModel, Field

from app.domain import DataSource  # noqa: F401  (확장 대비)


class ReportCreate(BaseModel):
    target_type: str = Field(..., description="shelter | dog")
    target_id: int
    description: str = Field(..., min_length=5, max_length=2000)
    image_url: str | None = None
    reporter_contact: str | None = None


class ReportCreated(BaseModel):
    id: int
    status: str = "pending"
    message: str = "신고가 접수되었습니다. 관리자 검토 후 반영됩니다."
