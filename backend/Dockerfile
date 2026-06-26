# PawTrace Backend Dockerfile (multi-stage, slim)
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 의존성 먼저 설치 (레이어 캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 + 마이그레이션/시드 스크립트
COPY app ./app
COPY migrations ./migrations
COPY scripts ./scripts
COPY alembic.ini ./alembic.ini

# 비루트 사용자로 실행 (보안)
RUN useradd -m appuser
USER appuser

EXPOSE 8000

# 컨테이너 헬스체크
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://localhost:8000/api/v1/health').status==200 else sys.exit(1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
