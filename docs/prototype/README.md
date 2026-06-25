# PawTrace — UI 프로토타입

새 비전("Today's Friend")을 반영한 정적 HTML 화면 프로토타입입니다. 빌드 없이 브라우저로 바로 열 수 있어요.

## 화면
| 파일 | 화면 |
|---|---|
| `index.html` | 홈 — Today's Friend (오늘의 친구) |
| `map.html` | 보호소 지도 — 시·도 선택 → 지역 상세 (2단계) |
| `passport.html` | Pet Passport 생애 타임라인 상세 |
| `guide.html` | AI 입양 가이드 |
| `style.css` | 공통 디자인 토큰(둥근/파스텔 테마) |
| `api.js` | **백엔드 API 연결 모듈** (점진적 향상 + 데모 폴백) |
| `korea_kr.png` | 남한 지도 일러스트(배경) |

## 실행
```bash
cd docs/prototype
python -m http.server 8777
# http://localhost:8777
```

## 백엔드 API 연결 (Live)
`api.js` 가 화면을 실제 API 데이터로 채웁니다. **백엔드가 없어도** HTML 에 박힌 데모 데이터가 그대로 보이고(화면 안 깨짐), 연결되면 자동으로 실데이터로 교체됩니다. 우상단 배지로 상태 표시:

- **● 실시간 API** — 백엔드 연결됨 (실데이터)
- **○ 데모 데이터** — 백엔드 미연결 (HTML 기본값)

연결되는 엔드포인트:
| 화면 | 호출 API |
|---|---|
| `index.html` | `GET /dogs/today`, `GET /dogs/{id}/passport` |
| `passport.html` | `GET /dogs/{id}/passport` (`?dog=2` 로 다른 강아지) |
| `map.html` | `GET /shelters?region=서울` (지역 클릭 시) |

API 주소 지정 우선순위: `?api=<url>` 쿼리 → `localStorage` → 기본값 `http://localhost:8000/api/v1`.

```bash
# 1) 백엔드 실행 (다른 터미널)
cd backend && uvicorn app.main:app --reload     # → http://localhost:8000

# 2) 프로토타입 실행 후 브라우저에서:
#    http://localhost:8777/index.html            (기본 localhost:8000 사용)
#    http://localhost:8777/map.html?api=http://<alb_dns_name>/api/v1   (클라우드 API 지정)
```

> ⚠️ 디자인/플로우 확인용 목업에서 출발했지만, 이제 실제 API 와 연결됩니다. 추후 Next.js 정식 구현 시 이 연결 패턴(폴백 포함)을 그대로 이식합니다.
