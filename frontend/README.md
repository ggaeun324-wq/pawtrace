# PawTrace Frontend (Next.js) — 스캐폴드

> 실제 구현 전 단계입니다. 현재 디자인/플로우는 `docs/prototype/` 의 정적 HTML로 확인할 수 있습니다.

## 폴더 구조
```
frontend/
  src/
    app/          # Next.js App Router 페이지 (오늘의 친구 / 지도 / passport / 가이드)
    components/   # Map, ShelterCard, PassportTimeline, ReportForm, HappyEndingCard
    lib/          # API 클라이언트 + Kakao Map 어댑터
    styles/       # 둥근/파스텔 디자인 토큰
```

## 백엔드 연동
- API Base: `http://localhost:8000/api/v1`
- 주요 호출: `GET /dogs/today`, `GET /shelters?region=`, `GET /dogs/{id}/passport`, `POST /reports`

## 다음 단계
2주차에 Next.js 프로젝트를 초기화하고 프로토타입 화면을 컴포넌트로 옮깁니다.
