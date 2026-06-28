"""헬스체크 (ALB / 컨테이너 readiness probe 용)."""
from fastapi import APIRouter

from app.core import cache

router = APIRouter()


@router.get("/health")
def health() -> dict:
    """기본 헬스체크. Redis 연결 상태도 함께 보고합니다(없어도 200).

    redis=true  → 캐시 연결 정상
    redis=false → 캐시 미연결(앱은 DB 폴백으로 정상 동작)
    """
    return {"status": "ok", "redis": cache.ping()}
