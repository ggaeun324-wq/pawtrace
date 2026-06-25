"""SQLAlchemy 세션/엔진.

DATABASE_URL 은 환경변수로 주입됩니다(core.config).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """FastAPI 의존성: 요청마다 세션을 열고 닫습니다."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
