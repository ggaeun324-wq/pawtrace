"""관리자 동기화 응답 스키마."""
from pydantic import BaseModel


class SyncResult(BaseModel):
    source_enabled: bool          # 공공데이터 키가 설정되어 실연동되었는지
    shelters_upserted: int
    dogs_total: int
    dogs_created: int
    dogs_updated: int
    message: str
