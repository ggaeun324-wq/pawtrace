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
        "thumbnail_url": None, "protect_end_date": "2026-07-06",
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
    {
        "id": 5, "name": "두유", "breed_label": "비글믹스(추정)", "breed_is_estimate": True,
        "age_estimate": "추정 1살", "gender": "male", "is_neutered": False,
        "adoption_status": AdoptionStatus.available, "shelter_id": 2,
        "thumbnail_url": None, "protect_end_date": "2026-06-29",
        "story": "호기심 많고 사람을 좋아하는 두유는 새 가족과의 첫 산책을 기다리고 있어요.",
    },
    {
        "id": 6, "name": "단비", "breed_label": "시츄(추정)", "breed_is_estimate": True,
        "age_estimate": "추정 6살", "gender": "female", "is_neutered": True,
        "adoption_status": AdoptionStatus.available, "shelter_id": 3,
        "thumbnail_url": None, "protect_end_date": "2026-07-01",
        "story": "조용하고 차분한 단비는 무릎에 앉아 있는 걸 가장 좋아해요.",
    },
    {
        "id": 7, "name": "모찌", "breed_label": "포메라니안(추정)", "breed_is_estimate": True,
        "age_estimate": "추정 2살", "gender": "female", "is_neutered": False,
        "adoption_status": AdoptionStatus.available, "shelter_id": 1,
        "thumbnail_url": None, "protect_end_date": "2026-07-03",
        "story": "작고 씩씩한 모찌는 처음 보는 사람에게도 금세 마음을 열어요.",
    },
    {
        "id": 8, "name": "바다", "breed_label": "리트리버믹스(추정)", "breed_is_estimate": True,
        "age_estimate": "추정 3살", "gender": "male", "is_neutered": True,
        "adoption_status": AdoptionStatus.available, "shelter_id": 2,
        "thumbnail_url": None, "protect_end_date": "2026-07-08",
        "story": "온순하고 듬직한 바다는 아이들과도 잘 지내는 다정한 친구예요.",
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
    5: [
        {"event_type": PassportEventType.rescue, "event_date": "2026-06-12",
         "title": "구조", "memo": "도로 근처에서 구조되었어요.",
         "source": DataSource.public_api},
        {"event_type": PassportEventType.intake, "event_date": "2026-06-13",
         "title": "보호소 입소", "memo": "포근한쉼터에서 보호를 시작했어요.",
         "source": DataSource.public_api},
        {"event_type": PassportEventType.available, "event_date": None,
         "title": "입양 가능", "memo": "지금 새로운 가족을 기다리고 있어요.",
         "source": DataSource.manual},
    ],
    6: [
        {"event_type": PassportEventType.rescue, "event_date": "2026-06-14",
         "title": "구조", "memo": "주택가에서 떠돌던 중 구조되었어요.",
         "source": DataSource.public_api},
        {"event_type": PassportEventType.intake, "event_date": "2026-06-15",
         "title": "보호소 입소", "memo": "함께걷개에서 보호를 시작했어요.",
         "source": DataSource.public_api},
        {"event_type": PassportEventType.available, "event_date": None,
         "title": "입양 가능", "memo": "조용한 가정을 기다리고 있어요.",
         "source": DataSource.manual},
    ],
    7: [
        {"event_type": PassportEventType.rescue, "event_date": "2026-06-16",
         "title": "구조", "memo": "시장 골목에서 시민이 발견했어요.",
         "source": DataSource.public_api},
        {"event_type": PassportEventType.intake, "event_date": "2026-06-17",
         "title": "보호소 입소", "memo": "햇살보호소에서 보호를 시작했어요.",
         "source": DataSource.public_api},
        {"event_type": PassportEventType.available, "event_date": None,
         "title": "입양 가능", "memo": "활발한 친구가 가족을 기다려요.",
         "source": DataSource.manual},
    ],
    8: [
        {"event_type": PassportEventType.rescue, "event_date": "2026-06-18",
         "title": "구조", "memo": "하천변에서 구조되었어요.",
         "source": DataSource.public_api},
        {"event_type": PassportEventType.intake, "event_date": "2026-06-19",
         "title": "보호소 입소", "memo": "포근한쉼터에서 보호를 시작했어요.",
         "source": DataSource.public_api},
        {"event_type": PassportEventType.available, "event_date": None,
         "title": "입양 가능", "memo": "듬직한 친구가 가족을 기다려요.",
         "source": DataSource.manual},
    ],
}

# --- PawTrace Academy 교육 콘텐츠 --------------------------------------------
# 책임 있는 입양 준비를 돕는 교육 + 퀴즈. 강아지를 추천하지 않습니다.
# 각 course: slug/title/emoji/summary/content/order_no + questions[]
# question: {question, options[], answer_index, explanation}
ACADEMY_COURSES = [
    {
        "slug": "mindset",
        "title": "입양 전 마음가짐",
        "emoji": "🌱",
        "order_no": 1,
        "summary": "입양은 10년 이상 함께하는 약속이에요. 시작 전에 꼭 생각해볼 것들.",
        "content": (
            "강아지 입양은 귀여움만으로 결정하기 어려운 '장기적인 약속'이에요. "
            "평균적으로 10~15년을 함께하게 되고, 그 시간 동안 산책·식사·병원·교육 등 "
            "꾸준한 돌봄이 필요해요.\n\n"
            "입양 전에는 우리 가족의 생활 패턴(외출 시간, 주거 형태, 함께 사는 사람), "
            "예상 비용(사료·예방접종·중성화·정기검진), 그리고 만약 아프거나 나이 들었을 때도 "
            "끝까지 함께할 수 있는지를 솔직하게 생각해보는 것이 좋아요.\n\n"
            "PawTrace는 '좋은 보호자/나쁜 보호자'를 평가하지 않아요. 다만 스스로 준비 상태를 "
            "돌아볼 수 있도록 돕는 것을 목표로 해요."
        ),
        "questions": [
            {
                "question": "강아지와 함께하는 기간으로 가장 현실적인 것은?",
                "options": ["6개월 정도", "2~3년", "10~15년 이상", "정해져 있지 않다"],
                "answer_index": 2,
                "explanation": "강아지는 보통 10년 이상 함께하는 가족이에요.",
            },
            {
                "question": "입양 전에 고려할 항목으로 적절하지 않은 것은?",
                "options": [
                    "우리 집 주거 형태와 생활 패턴",
                    "예방접종·중성화 등 예상 비용",
                    "강아지의 품종이 유행하는지 여부",
                    "아프거나 나이 들어도 함께할 수 있는지",
                ],
                "answer_index": 2,
                "explanation": "유행은 입양 기준이 될 수 없어요. 책임과 준비가 중요해요.",
            },
            {
                "question": "PawTrace Academy의 목적에 가장 가까운 것은?",
                "options": [
                    "좋은 보호자를 선발하기 위해",
                    "스스로 준비 상태를 돌아보도록 돕기 위해",
                    "강아지를 추천하기 위해",
                    "보호소 순위를 매기기 위해",
                ],
                "answer_index": 1,
                "explanation": "Academy는 평가가 아니라 준비를 돕는 콘텐츠예요.",
            },
        ],
    },
    {
        "slug": "care-basics",
        "title": "건강과 돌봄 기초",
        "emoji": "🩺",
        "order_no": 2,
        "summary": "예방접종, 중성화, 정기검진… 건강한 반려생활의 기본을 익혀요.",
        "content": (
            "강아지를 맞이하면 가장 먼저 동물병원에서 건강 상태를 확인하고, 나이에 맞는 "
            "예방접종 계획을 세우는 것이 좋아요. 심장사상충 예방, 구충, 정기검진도 "
            "꾸준히 챙겨주세요.\n\n"
            "중성화는 질병 예방과 행동 안정에 도움이 될 수 있어요. 보호소나 수의사와 "
            "상담해 시기를 결정하면 좋아요.\n\n"
            "균형 잡힌 식사와 적절한 운동(산책), 그리고 깨끗한 환경은 강아지의 몸과 "
            "마음 건강 모두에 중요해요."
        ),
        "questions": [
            {
                "question": "강아지를 처음 맞이했을 때 가장 먼저 하면 좋은 것은?",
                "options": [
                    "바로 미용실에 데려간다",
                    "동물병원에서 건강 상태를 확인한다",
                    "친구들에게 자랑한다",
                    "사진을 SNS에 올린다",
                ],
                "answer_index": 1,
                "explanation": "건강 확인과 예방접종 계획이 먼저예요.",
            },
            {
                "question": "꾸준히 챙겨야 하는 예방 관리가 아닌 것은?",
                "options": ["심장사상충 예방", "정기검진", "구충", "매일 미용"],
                "answer_index": 3,
                "explanation": "미용은 매일 할 필요는 없어요. 예방·검진이 핵심이에요.",
            },
            {
                "question": "중성화에 대한 설명으로 가장 적절한 것은?",
                "options": [
                    "무조건 해선 안 된다",
                    "질병 예방·행동 안정에 도움이 될 수 있어 상담 후 결정한다",
                    "보호자가 임의로 시기를 정하면 안 된다는 규정은 없다",
                    "건강과 전혀 관련이 없다",
                ],
                "answer_index": 1,
                "explanation": "수의사·보호소와 상담해 시기를 정하는 것이 좋아요.",
            },
        ],
    },
    {
        "slug": "socialization",
        "title": "사회화와 적응",
        "emoji": "🐾",
        "order_no": 3,
        "summary": "새 가족과 집에 적응하는 시간, 천천히 신뢰를 쌓는 방법.",
        "content": (
            "보호소에서 온 강아지는 새로운 환경에 적응할 시간이 필요해요. 처음 며칠은 "
            "조용하고 안전한 공간을 마련해주고, 과한 스킨십보다 강아지가 먼저 다가올 때까지 "
            "기다려 주는 것이 좋아요.\n\n"
            "사회화는 다양한 사람·소리·환경을 '긍정적인 경험'으로 천천히 만나게 하는 과정이에요. "
            "겁이 많은 친구라면 더 천천히, 칭찬과 간식으로 신뢰를 쌓아가요.\n\n"
            "적응 속도는 강아지마다 다르니, 비교하지 않고 그 아이의 속도를 존중해 주세요."
        ),
        "questions": [
            {
                "question": "보호소에서 온 강아지를 맞이한 첫 며칠 동안 좋은 태도는?",
                "options": [
                    "최대한 많이 안아주고 사람들을 초대한다",
                    "조용하고 안전한 공간에서 천천히 적응하게 한다",
                    "바로 강아지 카페에 데려간다",
                    "다른 강아지들과 곧장 어울리게 한다",
                ],
                "answer_index": 1,
                "explanation": "처음엔 안정이 우선이에요. 강아지의 속도를 존중해요.",
            },
            {
                "question": "사회화 과정에 대한 설명으로 가장 적절한 것은?",
                "options": [
                    "겁을 빨리 없애려 강하게 노출시킨다",
                    "다양한 경험을 긍정적으로 천천히 만나게 한다",
                    "한 번에 끝내야 한다",
                    "모든 강아지가 같은 속도로 적응한다",
                ],
                "answer_index": 1,
                "explanation": "사회화는 긍정적 경험을 천천히 쌓는 과정이에요.",
            },
            {
                "question": "적응 속도에 대한 바른 생각은?",
                "options": [
                    "다른 강아지와 비교해 빠르게 만든다",
                    "그 아이의 속도를 존중한다",
                    "느리면 입양이 잘못된 것이다",
                    "정해진 기간 안에 끝나야 한다",
                ],
                "answer_index": 1,
                "explanation": "적응 속도는 저마다 달라요. 비교하지 않아요.",
            },
        ],
    },
]
