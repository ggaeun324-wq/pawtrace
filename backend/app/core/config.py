"""환경설정 (12-factor).

민감한 값(DB 비밀번호, AI 키 등)은 코드가 아니라 환경변수/.env 로 주입합니다.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "PawTrace API"
    APP_VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"

    # 콤마로 구분된 허용 오리진 (예: "http://localhost:3000")
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8777"]

    # DB / 캐시 (실제 연결 시 사용)
    DATABASE_URL: str = "postgresql+psycopg2://pawtrace:pawtrace@db:5432/pawtrace"
    REDIS_URL: str = "redis://cache:6379/0"

    # 인증(JWT). 운영에서는 반드시 환경변수로 강력한 시크릿을 주입하세요.
    JWT_SECRET: str = "dev-only-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 토큰 유효기간(분) = 24시간
    # 시드로 생성되는 플랫폼 관리자 계정(데모용). 운영에서는 환경변수로 교체.
    ADMIN_EMAIL: str = "admin@pawtrace.dev"
    ADMIN_PASSWORD: str = "admin1234"

    # 외부 연동 (값이 없으면 stub 모드로 동작)
    PUBLIC_DATA_API_KEY: str | None = None
    # 농림축산검역본부 유기동물 조회 서비스(data.go.kr) 엔드포인트.
    PUBLIC_DATA_BASE_URL: str = (
        "https://apis.data.go.kr/1543061/abandonmentPublicSrvc/abandonmentPublic"
    )
    # 주소→좌표 변환(지오코딩)용 카카오 REST 키. 없으면 좌표는 비워둡니다.
    KAKAO_REST_API_KEY: str | None = None
    AWS_S3_BUCKET: str | None = None
    BEDROCK_MODEL_ID: str | None = None


settings = Settings()
