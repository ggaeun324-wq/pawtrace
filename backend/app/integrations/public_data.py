"""공공데이터(유기동물) 연동 어댑터.

출처: 농림축산검역본부 '유기동물 조회 서비스' (data.go.kr).
- HTTP 호출부(fetch_raw)와 순수 파싱부(parse_animals)를 분리했습니다.
  → 파싱은 API 키 없이도 저장된 샘플 응답으로 단위 테스트가 가능합니다.
- 멱등 동기화: 강아지는 desertionNo(유기번호), 보호소는 보호소명을 external_id 로
  사용해 upsert 합니다(중복 방지). (관리자 POST /admin/sync/public-data)

주의(서비스 원칙):
- 공공데이터를 그대로 '사실'로 단정하지 않고 출처(source=public_api)를 표기합니다.
- 좌표(lat/lng)는 이 API 에 없으므로, 카카오 지오코딩 키가 있을 때만 별도로 채웁니다.
"""
from __future__ import annotations

import httpx

from app.core.config import settings
from app.domain import AdoptionStatus, DataSource

# 공공 API 코드 → PawTrace 도메인 값 매핑 -------------------------------------
_SEX = {"M": "male", "F": "female", "Q": "unknown"}
_NEUTER = {"Y": True, "N": False, "U": None}


def _map_adoption_status(process_state: str | None) -> AdoptionStatus:
    """processState(보호상태) → 우리 입양상태.
    - '보호중' → 입양 가능(available)
    - '입양' 포함 종료 → 입양 완료(adopted)
    - 그 외/미상 → 보호중(protected)
    """
    s = process_state or ""
    if "보호중" in s:
        return AdoptionStatus.available
    if "입양" in s:
        return AdoptionStatus.adopted
    return AdoptionStatus.protected


def _clean_breed(kind_cd: str | None) -> str | None:
    """'[개] 믹스견' → '믹스견'. 종 머리표([개]/[고양이])를 제거."""
    if not kind_cd:
        return None
    label = kind_cd.split("]", 1)[-1].strip() if "]" in kind_cd else kind_cd.strip()
    return label or None


def _as_item_list(payload: dict) -> list[dict]:
    """응답에서 item 배열을 안전 추출. items 가 비었거나 단일 dict 여도 처리."""
    body = (payload or {}).get("response", {}).get("body", {})
    items = body.get("items") or {}
    if not items:
        return []
    item = items.get("item")
    if item is None:
        return []
    return item if isinstance(item, list) else [item]


def parse_animals(payload: dict) -> list[dict]:
    """공공 API JSON → PawTrace 친화 dict 목록 (순수 함수, 테스트 대상).

    반환 dict 구조:
      shelter: {external_id, name, region, address, phone}
      dog:     {external_id, name, breed_label, gender, is_neutered,
                adoption_status, thumbnail_url, story}
    """
    results: list[dict] = []
    for it in _as_item_list(payload):
        care_nm = (it.get("careNm") or "").strip()
        if not care_nm:
            continue  # 보호소명이 없으면 신뢰도 낮음 → 건너뜀

        desertion_no = str(it.get("desertionNo") or "").strip()
        breed = _clean_breed(it.get("kindCd"))
        special = (it.get("specialMark") or "").strip()

        results.append(
            {
                "shelter": {
                    "external_id": care_nm,  # 보호소명을 안정 키로 사용
                    "name": care_nm,
                    "region": (it.get("orgNm") or "").strip() or "미상",
                    "address": (it.get("careAddr") or "").strip() or None,
                    "phone": (it.get("careTel") or "").strip() or None,
                },
                "dog": {
                    "external_id": desertion_no or None,
                    # 공공데이터에 개체명이 없어 유기번호 기반 임시 이름 부여.
                    "name": f"보호견 {desertion_no[-4:]}" if desertion_no else "보호견",
                    "breed_label": breed,
                    "gender": _SEX.get((it.get("sexCd") or "").strip(), "unknown"),
                    "is_neutered": _NEUTER.get((it.get("neuterYn") or "").strip()),
                    "adoption_status": _map_adoption_status(it.get("processState")),
                    "thumbnail_url": (it.get("popfile") or it.get("popfile1") or "").strip()
                    or None,
                    "story": special or None,
                },
            }
        )
    return results


def fetch_raw(
    *, begin: str | None = None, end: str | None = None, rows: int = 50, page: int = 1
) -> dict:
    """공공 API 호출 → 원본 JSON. 키 없으면 빈 응답.

    begin/end 는 'YYYYMMDD' 발견일 범위(선택). upkind=417000 = 개.
    """
    if not settings.PUBLIC_DATA_API_KEY:
        return {}
    params = {
        "serviceKey": settings.PUBLIC_DATA_API_KEY,
        "_type": "json",
        "numOfRows": rows,
        "pageNo": page,
        "upkind": "417000",  # 개
    }
    if begin:
        params["bgnde"] = begin
    if end:
        params["endde"] = end
    with httpx.Client(timeout=10) as client:
        resp = client.get(settings.PUBLIC_DATA_BASE_URL, params=params)
        resp.raise_for_status()
        return resp.json()


def fetch_animals(
    *, begin: str | None = None, end: str | None = None, rows: int = 50, page: int = 1
) -> list[dict]:
    """공공 API 호출 + 파싱까지 한 번에. 키 없으면 빈 목록."""
    return parse_animals(fetch_raw(begin=begin, end=end, rows=rows, page=page))


def is_enabled() -> bool:
    """공공데이터 키가 설정되어 실연동이 가능한지 여부."""
    return bool(settings.PUBLIC_DATA_API_KEY)


SOURCE = DataSource.public_api

