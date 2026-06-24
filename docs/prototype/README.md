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
| `korea_kr.png` | 남한 지도 일러스트(배경) |

## 실행
```bash
cd docs/prototype
python -m http.server 8777
# http://localhost:8777
```

> ⚠️ 디자인/플로우 확인용 정적 목업입니다. 실제 데이터·기능은 없으며, 추후 Next.js로 구현 시 참고용으로 사용합니다.
