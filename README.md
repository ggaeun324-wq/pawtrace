<div align="center">

# 🐾 PawTrace

### *Know where every paw begins.*

보호소와 강아지의 **이력을 지도와 타임라인으로 투명하게** 보여주어,
신뢰할 수 있는 입양 문화를 돕는 플랫폼입니다.

</div>

---

## 🌟 PawTrace는 무엇이 다른가요?

기존 입양 앱들은 대부분 **"지금 입양 가능한 아이 목록"** 을 보여주는 데 그칩니다.
PawTrace는 **목록이 아니라 "이력과 신뢰"** 를 보여줍니다.

| | 기존 입양 앱 | 🐾 PawTrace |
|---|---|---|
| 핵심 | 입양 가능한 강아지 목록(스냅샷) | 강아지의 **출처와 이력 타임라인** |
| 신뢰 | 보호소 정보 나열 | **투명성 지표(신뢰도 점수)** + 근거 공개 |
| 데이터 | 일방향 제공 | 사용자 신고 → 관리자 검증 **참여형 루프** |
| 정보 해소 | 직접 읽어야 함 | **AI 요약·분류**로 정보 비대칭 완화 |

> 한 줄 차별점: **다른 앱은 '입양 가능한 강아지'를 보여주고, PawTrace는 '믿을 수 있는 출처와 이력'을 보여줍니다.**

---

## ✨ 핵심 기능

- 🗺️ **지도 기반 보호소 검색** — 현재 위치/지역 기준, 정부 등록 여부·신뢰도 표시
- 🐶 **강아지 이력 타임라인** — 구조 → 입소 → 건강검진 → 예방접종 → 중성화 → 입양
- 🙋 **신고/검증 시스템** — 사용자가 의심 사례를 신고하면 관리자가 검토 후 신뢰도에 반영
- 🤖 **AI 보조** — 신고 분류, 보호소 설명 요약(이상 징후 키워드 탐지는 확장 단계)
- 🛠️ **관리자 기능** — 보호소·강아지·신고·신뢰도 관리

> ⚖️ PawTrace는 특정 업체를 "불법"으로 단정하지 않습니다. 공공데이터·사용자 신고·관리자 검증에 기반한
> **"검증 필요 / 투명성 낮음 / 공공데이터 불일치"** 같은 **투명성 지표**로만 표현합니다.

---

## 🧱 기술 스택

| 영역 | 기술 |
|---|---|
| Frontend | Next.js, Kakao Map SDK |
| Backend | FastAPI (Python) |
| Database | PostgreSQL + PostGIS |
| Cache | Redis |
| AI | Azure OpenAI / OpenAI API |
| Infra | Docker, Azure Container Apps (→ AKS 확장) |
| CI/CD | GitHub Actions |

---

## 🏗️ 아키텍처 (개요)

```
[ Next.js + Kakao Map ]
        │ REST
        ▼
[ FastAPI ] ── [ PostgreSQL + PostGIS ]  (보호소/강아지/이력/신고)
   │      └──── [ Redis ]                 (지도 검색 캐싱)
   └──────────── [ Azure OpenAI ]         (신고 분류 · 요약)
        │
        ▼
[ Azure Blob Storage ]  (신고 이미지)

[ GitHub Actions ] → Docker build → ACR → Azure Container Apps
```

---

## 🚀 로컬 실행 방법

> ⚠️ 아직 초기 개발 단계입니다. 아래는 목표 실행 흐름입니다.

```bash
# 1. 저장소 클론
git clone https://github.com/ggaeun324-wq/pawtrace.git
cd pawtrace

# 2. 환경변수 설정 (.env.example 복사 후 값 입력)
cp .env.example .env

# 3. Docker로 전체 스택 실행 (api + postgres/postgis + redis)
docker-compose up --build

# 4. 접속
# - API 문서:   http://localhost:8000/docs
# - 프론트엔드: http://localhost:3000
```

> 🔐 API 키·DB 비밀번호 등 민감한 값은 모두 `.env`(환경변수)로 분리하며 저장소에 커밋하지 않습니다.

---

## 🗓️ 개발 로드맵 (4주 MVP)

| 주차 | 목표 |
|---|---|
| 1주차 | 기획 · DB(PostGIS) · 기본 조회 API · Docker 로컬 구동 |
| 2주차 | 지도 · 보호소 검색 · 강아지 이력 타임라인 |
| 3주차 | 신고 · 관리자 검증 · 신뢰도 반영 · AI 분류 |
| 4주차 | GitHub Actions CI/CD · Azure 배포 · 문서 정리 |

진행 상황은 [Issues](https://github.com/ggaeun324-wq/pawtrace/issues)와 [Milestones](https://github.com/ggaeun324-wq/pawtrace/milestones)에서 확인할 수 있습니다.

---

## 🤝 기여 & 윤리 원칙

- 본 서비스의 신뢰도 점수는 **참고용 투명성 지표**이며 법적 판단이 아닙니다.
- 신고는 즉시 공개 반영되지 않고 **관리자 검증 후** 반영됩니다.
- 개인정보는 최소 수집하며, 업로드 이미지의 위치정보(EXIF)는 제거합니다.

---

<div align="center">

*Made with 🐾 for a more transparent adoption culture.*

</div>