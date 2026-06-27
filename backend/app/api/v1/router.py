"""v1 라우터 집계.

각 도메인 라우트를 하나로 묶어 main.py 에서 한 번에 연결합니다.
"""
from fastapi import APIRouter

from app.api.v1.routes import (
    academy,
    admin,
    auth,
    dogs,
    health,
    reports,
    shelter_ai,
    shelters,
    trust,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(dogs.router, prefix="/dogs", tags=["dogs"])
api_router.include_router(shelters.router, prefix="/shelters", tags=["shelters"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(academy.router, prefix="/academy", tags=["academy"])
api_router.include_router(trust.router, prefix="/trust", tags=["trust"])
api_router.include_router(shelter_ai.router, prefix="/shelter", tags=["shelter-ai"])
