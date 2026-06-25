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

    # 프론트엔드(Next.js)에서의 호출 허용. 운영에서는 도메인을 좁힙니다.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    return app


app = create_app()
