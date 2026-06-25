"""공공데이터(유기동물) 연동 (stub).

출처: 공공데이터포털 / APMS 유기동물 Open API.
멱등 동기화: external_id 기준 upsert 로 중복을 방지합니다. (관리자 POST /admin/sync/public)
"""
from app.core.config import settings


def fetch_animals(region: str | None = None) -> list[dict]:
    if not settings.PUBLIC_DATA_API_KEY:
        return []  # 키 없으면 빈 결과 (로컬은 시드 데이터 사용)
    raise NotImplementedError("공공데이터 동기화는 1~2주차에 구현합니다.")
