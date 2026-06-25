# PawTrace Backend (FastAPI)

Clean Architecture 기반 백엔드. MVP는 **시드 데이터로 즉시 동작**하며, 이후 RDS(PostgreSQL/PostGIS)로 전환합니다.

## 레이어
```
api (라우터)  →  services (유스케이스)  →  repositories (DB 추상화)  →  models / DB
                                          integrations/ : 공공데이터 · Bedrock · S3 (격리)
```

## 폴더
```
backend/app/
  core/          설정(config)
  domain/        enum / 도메인 규칙 (점수·랭킹 없음)
  schemas/       Pydantic request/response 계약
  models/        SQLAlchemy ORM (DB 스키마)
  repositories/  데이터 접근 (현재 seed → 추후 DB 쿼리)
  services/      비즈니스 로직
  api/v1/routes/ HTTP 엔드포인트
  integrations/  외부 연동 stub
```

## 로컬 실행
```bash
# A) Docker (권장)
docker compose up --build        # → http://localhost:8000/docs

# B) 직접 실행
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 테스트 / 린트
```bash
pytest          # API 스모크 테스트
ruff check .    # 린트
```

## 주요 엔드포인트 (/api/v1)
| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/health` | 헬스체크 |
| GET | `/dogs/today` | 오늘의 친구 |
| GET | `/dogs/{id}/passport` | 생애 타임라인 |
| GET | `/shelters?region=서울` | 지역 보호소 목록(+입양가능 수) |
| GET | `/shelters/{id}` | 보호소 상세 |
| POST | `/reports` | 신고 접수 |
