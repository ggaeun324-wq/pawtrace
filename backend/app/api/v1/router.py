"""v1 라우터 집계.

각 도메인 라우트를 하나로 묶어 main.py 에서 한 번에 연결합니다.
"""
from fastapi import APIRouter

from app.api.v1.routes import dogs, health, reports, shelters

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(dogs.router, prefix="/dogs", tags=["dogs"])
api_router.include_router(shelters.router, prefix="/shelters", tags=["shelters"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
