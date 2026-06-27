"""카카오 지오코딩 어댑터 (주소 → 위경도 좌표).

용도:
- 공공데이터로 받은 보호소는 주소만 있고 좌표가 없습니다.
- 지도에 보호소 핀을 찍으려면 위경도가 필요하므로, 카카오 로컬 API 로 변환합니다.

설계:
- 키가 없으면(stub 모드) 조용히 None 을 반환합니다(동기화는 계속 진행).
- 네트워크/파싱 오류도 None 으로 흡수합니다 — 좌표는 '있으면 좋은' 부가정보이지,
  동기화를 실패시킬 만큼 필수는 아니기 때문입니다.
- 카카오는 (경도=x, 위도=y) 순서로 반환합니다. 헷갈리기 쉬우니 명시적으로 매핑합니다.
"""
from __future__ import annotations

import httpx

from app.core.config import settings

_KAKAO_ADDRESS_URL = "https://dapi.kakao.com/v2/local/search/address.json"
_KAKAO_KEYWORD_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"


def is_enabled() -> bool:
    """카카오 REST 키가 설정되어 실제 지오코딩이 가능한지 여부."""
    return bool(settings.KAKAO_REST_API_KEY)


def _first_coord(payload: dict) -> tuple[float, float] | None:
    """카카오 응답 documents[0] 에서 (lat, lng) 추출. 비면 None."""
    docs = (payload or {}).get("documents") or []
    if not docs:
        return None
    doc = docs[0]
    try:
        # x=경도(lng), y=위도(lat)
        lng = float(doc["x"])
        lat = float(doc["y"])
    except (KeyError, TypeError, ValueError):
        return None
    return lat, lng


def geocode(address: str | None) -> tuple[float, float] | None:
    """주소 문자열 → (위도, 경도). 키 없음/실패 시 None.

    1) 주소 검색(정확)으로 먼저 시도하고,
    2) 결과가 없으면 키워드 검색(보호소명 등 비정형 주소 대응)으로 한 번 더 시도합니다.
    """
    addr = (address or "").strip()
    if not addr or not is_enabled():
        return None

    headers = {"Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY}"}
    try:
        with httpx.Client(timeout=5, headers=headers) as client:
            resp = client.get(_KAKAO_ADDRESS_URL, params={"query": addr})
            resp.raise_for_status()
            coord = _first_coord(resp.json())
            if coord is not None:
                return coord
            # 주소 검색 실패 → 키워드 검색으로 보강
            resp2 = client.get(_KAKAO_KEYWORD_URL, params={"query": addr})
            resp2.raise_for_status()
            return _first_coord(resp2.json())
    except (httpx.HTTPError, ValueError):
        return None
