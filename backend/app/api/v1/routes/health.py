"""헬스체크 (ALB / 컨테이너 readiness probe 용)."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}
