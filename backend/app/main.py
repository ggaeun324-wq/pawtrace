"""애플리케이션 진입점.

FastAPI 앱을 생성하고 v1 라우터를 연결합니다.
실행: `uvicorn app.main:app --reload`
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="PawTrace — Pet Life Transparency Platform API",
    )

    # 프론트엔드에서의 호출 허용. 운영에서는 도메인을 좁힙니다.
    # 로컬 개발은 localhost / 127.0.0.1 의 임의 포트를 정규식으로 허용합니다.
    # (예: 프로토타입 8777, Next.js 3000 — 두 호스트명 모두 커버)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    return app


app = create_app()
