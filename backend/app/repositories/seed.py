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
    {
        "id": 2, "name": "초코", "breed_label": "푸들(추정)", "breed_is_estimate": True,
        "age_estimate": "추정 4살", "gender": "male", "is_neutered": True,
        "adoption_status": AdoptionStatus.adopted, "shelter_id": 2,
        "thumbnail_url": None,
        "story": "오래 기다린 초코는 따뜻한 가족을 만나 매일 산책을 즐기고 있어요.",
    },
    {
        "id": 3, "name": "보리", "breed_label": "진도믹스(추정)", "breed_is_estimate": True,
        "age_estimate": "추정 3살", "gender": "female", "is_neutered": True,
        "adoption_status": AdoptionStatus.adopted, "shelter_id": 3,
        "thumbnail_url": None,
        "story": "겁이 많던 보리는 새 가족의 사랑으로 활발한 강아지가 되었답니다.",
    },
    {
        "id": 4, "name": "구름", "breed_label": "말티즈(추정)", "breed_is_estimate": True,
        "age_estimate": "추정 5살", "gender": "male", "is_neutered": False,
        "adoption_status": AdoptionStatus.adopted, "shelter_id": 1,
        "thumbnail_url": None,
        "story": "구름이는 입양 후 첫 생일파티를 하며 행복한 하루를 보냈어요.",
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
    ],
    2: [
        {"event_type": PassportEventType.intake, "event_date": "2025-11-02",
         "title": "보호소 입소", "memo": "포근한쉼터에서 보호를 시작했어요.",
         "source": DataSource.manual},
        {"event_type": PassportEventType.adopted, "event_date": "2026-03-15",
         "title": "입양 완료", "memo": "따뜻한 가족을 만나 행복하게 지내고 있어요.",
         "source": DataSource.manual},
    ],
    3: [
        {"event_type": PassportEventType.intake, "event_date": "2025-12-20",
         "title": "보호소 입소", "memo": "함께걷개에서 보호를 시작했어요.",
         "source": DataSource.manual},
        {"event_type": PassportEventType.adopted, "event_date": "2026-04-01",
         "title": "입양 완료", "memo": "새 가족과 매일 산책하며 지내요.",
         "source": DataSource.manual},
    ],
    4: [
        {"event_type": PassportEventType.intake, "event_date": "2025-10-05",
         "title": "보호소 입소", "memo": "햇살보호소에서 보호를 시작했어요.",
         "source": DataSource.manual},
        {"event_type": PassportEventType.adopted, "event_date": "2026-02-28",
         "title": "입양 완료", "memo": "첫 생일파티를 하며 가족이 되었어요.",
         "source": DataSource.manual},
    ],
}
