"""시드 데이터 (MVP 데모용).

TODO: 실제 운영에서는 RDS(PostgreSQL/PostGIS) + 공공데이터 동기화로 대체합니다.
프론트 프로토타입(봄이, 햇살보호소)과 값을 맞춰 두었습니다.
"""
from app.domain import (
    AdoptionStatus,
    DataSource,
    PassportEventType,
    TransparencyLevel,
)

SHELTERS = [
    {
        "id": 1, "name": "햇살보호소", "region": "서울",
        "address": "서울 마포구", "lat": 37.5563, "lng": 126.9236,
        "is_gov_registered": True, "transparency_level": TransparencyLevel.verified,
        "description": "공공데이터와 일치 확인된 보호소입니다.",
        "phone": "02-000-0000", "gov_reg_no": "SEOUL-2024-001",
    },
    {
        "id": 2, "name": "포근한쉼터", "region": "서울",
        "address": "서울 은평구", "lat": 37.6027, "lng": 126.9291,
        "is_gov_registered": True, "transparency_level": TransparencyLevel.basic,
        "description": "기본 정보가 확인된 보호소입니다.",
        "phone": "02-111-1111", "gov_reg_no": "SEOUL-2024-014",
    },
    {
        "id": 3, "name": "함께걷개", "region": "서울",
        "address": "서울 성동구", "lat": 37.5634, "lng": 127.0369,
        "is_gov_registered": False, "transparency_level": TransparencyLevel.unverified,
        "description": "공개 정보가 부족합니다. (의심이 아니라 정보 부족)",
        "phone": None, "gov_reg_no": None,
    },
]

DOGS = [
    {
        "id": 1, "name": "봄이", "breed_label": "믹스(추정)", "breed_is_estimate": True,
        "age_estimate": "추정 2살", "gender": "female", "is_neutered": True,
        "adoption_status": AdoptionStatus.available, "shelter_id": 1,
        "thumbnail_url": None,
        "story": "추운 겨울 공원에서 구조된 봄이는 지금은 누구보다 다정한 친구가 되었어요.",
    },
]

PASSPORT_EVENTS = {
    1: [
        {"event_type": PassportEventType.rescue, "event_date": "2026-01-08",
         "title": "구조", "memo": "마포구 공원에서 시민이 발견해 신고했어요.",
         "source": DataSource.public_api},
        {"event_type": PassportEventType.intake, "event_date": "2026-01-09",
         "title": "보호소 입소", "memo": "햇살보호소로 옮겨졌어요.",
         "source": DataSource.public_api},
        {"event_type": PassportEventType.vaccination, "event_date": "2026-02-10",
         "title": "예방접종", "memo": "종합 백신 접종 완료.",
         "source": DataSource.manual},
        {"event_type": PassportEventType.neuter, "event_date": "2026-02-24",
         "title": "중성화", "memo": "수술 후 안정적으로 회복했어요.",
         "source": DataSource.manual},
        {"event_type": PassportEventType.available, "event_date": None,
         "title": "입양 가능", "memo": "평생 가족을 기다리고 있어요.",
         "source": DataSource.manual},
    ]
}
