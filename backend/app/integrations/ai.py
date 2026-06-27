"""Amazon Bedrock AI 연동 (P2 stub).

원칙: AI는 강아지를 점수화·랭킹하지 않습니다. 추정값은 'estimate'로 표기합니다.
실제 호출은 boto3 bedrock-runtime invoke_model 로 구현하며,
IAM Task Role 에 bedrock:InvokeModel 만 부여합니다(keyless).
결과는 ElastiCache 로 캐싱해 비용을 줄입니다.
"""
from app.core.config import settings


def summarize(text: str) -> str:
    """설명/후기 요약. (stub)"""
    if not settings.BEDROCK_MODEL_ID:
        return text[:120] + ("…" if len(text) > 120 else "")
    raise NotImplementedError("Bedrock 호출은 P2에서 구현합니다.")


def classify_report(description: str) -> str:
    """신고 내용 분류. (stub)"""
    return "uncategorized"


# 입양 전 자기 점검 보조에 쓰는 기본 질문/준비사항(가치판단 없는 중립 문구).
_BASE_REFLECTION_QUESTIONS = [
    "하루 중 강아지와 함께 있어줄 수 있는 시간은 어느 정도인가요?",
    "산책, 식사, 배변 관리 등 매일의 돌봄을 누가 책임질 수 있나요?",
    "예방접종·중성화·정기검진 등 의료 비용을 감당할 준비가 되어 있나요?",
    "이사, 이직, 가족 구성 변화가 생겨도 함께할 수 있나요?",
    "강아지가 아프거나 나이 들었을 때도 끝까지 함께할 수 있나요?",
]
_BASE_REFLECTION_CHECKLIST = [
    "동물병원 위치와 예상 진료 비용 확인하기",
    "한 달 양육 비용(사료·간식·용품·의료) 가볍게 계산해보기",
    "강아지가 안전하게 지낼 공간 점검하기",
    "가족 구성원 모두와 입양에 대해 이야기 나누기",
]


def adoption_reflection(situation: str) -> dict:
    """입양 전 '생각해볼 질문 + 준비사항'을 정리합니다(추천 아님).

    원칙:
    - 특정 강아지/품종/보호소를 추천하지 않습니다.
    - 사람을 '좋은/나쁜 보호자'로 평가하지 않습니다.
    - 사용자가 적은 상황 키워드에 맞춰 점검 항목을 보태주는 보조 역할만 합니다.

    Bedrock 키가 없으면 규칙 기반으로 동작합니다(데모/테스트 가능).
    """
    questions = list(_BASE_REFLECTION_QUESTIONS)
    checklist = list(_BASE_REFLECTION_CHECKLIST)

    # 상황 키워드별 추가 점검 항목(중립적 안내).
    if any(k in situation for k in ("아파트", "빌라", "원룸", "오피스텔")):
        questions.append("공동주택이라면 이웃·소음·반려동물 규정도 함께 살펴보셨나요?")
    if any(k in situation for k in ("아이", "아기", "어린이", "유아")):
        questions.append("어린 자녀와 강아지가 안전하게 지내도록 어떤 준비를 할 수 있을까요?")
    if any(k in situation for k in ("직장", "출근", "회사", "야근", "혼자")):
        questions.append("집을 비우는 시간 동안 강아지의 외로움·배변은 어떻게 도울 수 있을까요?")
    if any(k in situation for k in ("처음", "초보", "경험 없")):
        checklist.append("기본 교육·사회화 자료를 미리 읽어보기")

    note = (
        "이 정리는 참고용이에요. PawTrace는 강아지를 추천하거나 보호자를 평가하지 않아요. "
        "스스로 준비 상태를 돌아보는 데 활용해 주세요."
    )
    return {"questions": questions, "checklist": checklist, "note": note}


def trust_summary(facts: dict) -> str:
    """입양 준비 활동을 '객관적으로' 요약합니다(평가 아님).

    원칙:
    - '좋은/나쁜 보호자' 같은 가치판단 표현을 쓰지 않습니다.
    - 사실(가입 기간, 교육 수료 수, 체크리스트 진행, 프로필 작성률)만 나열합니다.
    - 최종 판단은 보호소 직원의 몫임을 명시합니다.

    Bedrock 키가 없으면 규칙 기반 문장으로 동작합니다.
    """
    parts: list[str] = []
    days = facts.get("days_since_join", 0)
    parts.append(f"가입 후 약 {days}일째 활동 중이에요.")

    badges = facts.get("education_count", 0)
    if badges:
        parts.append(f"교육 과정 {badges}개를 수료했어요.")
    else:
        parts.append("아직 수료한 교육 과정은 없어요.")

    done = facts.get("checklist_completed", 0)
    total = facts.get("checklist_total", 5)
    parts.append(f"입양 준비 체크리스트는 {total}개 중 {done}개를 완료했어요.")

    comp = facts.get("profile_completeness", 0)
    parts.append(f"프로필은 {comp}% 작성되어 있어요.")

    if facts.get("has_life_record"):
        parts.append("입양 후 반려생활 기록도 남기고 있어요.")

    parts.append("이 요약은 참고용 활동 정리이며, 최종 판단은 보호소에서 해주세요.")
    return " ".join(parts)


# Shelter AI Assistant — 강아지 등록 보조용 키워드 풀(중립적 표현).
_TEMPERAMENT_MAP = {
    "활발": "활발한",
    "에너지": "에너지가 넘치는",
    "온순": "온순한",
    "차분": "차분한",
    "조용": "조용한",
    "애교": "애교 많은",
    "사람": "사람을 잘 따르는",
    "겁": "조심성 있는",
    "소심": "낯을 조금 가리는",
    "호기심": "호기심 많은",
}


def dog_intro_draft(hints: dict) -> dict:
    """보호소 직원의 강아지 등록을 돕는 '초안'을 생성합니다(자동 게시 아님).

    원칙:
    - 결과는 어디까지나 '초안'이며, 보호소 직원이 반드시 확인/수정 후 저장합니다.
    - 외형·성격은 추정(estimate)으로 표기하고 단정하지 않습니다.
    - 강아지를 점수화하거나 입양을 유도/과장하는 표현을 쓰지 않습니다.

    실제 운영에서는 사진을 Bedrock 비전 모델로 분석하지만,
    키가 없으면 직원이 입력한 힌트를 바탕으로 규칙 기반 초안을 만듭니다.
    """
    name = (hints.get("name") or "").strip() or "이 친구"
    breed = (hints.get("breed_hint") or "").strip() or "믹스"
    color = (hints.get("color_hint") or "").strip()
    temperament = (hints.get("temperament_hint") or "").strip()

    # 외형 초안(추정). 색상 힌트가 있으면 반영, 없으면 직원이 채우도록 안내.
    appearance_bits = []
    if color:
        appearance_bits.append(f"{color} 계열의 털")
    appearance_bits.append(f"{breed}(품종 추정)")
    appearance = " · ".join(appearance_bits)

    # 성격 키워드 초안. 힌트 키워드를 중립 표현으로 변환, 없으면 기본 세트.
    keywords: list[str] = []
    for key, label in _TEMPERAMENT_MAP.items():
        if key in temperament:
            keywords.append(label)
    if not keywords:
        keywords = ["사람을 잘 따르는", "새로운 환경에 적응 중인"]
    keywords = list(dict.fromkeys(keywords))[:4]  # 중복 제거 + 최대 4개

    personality_phrase = ", ".join(keywords)
    intro = (
        f"{name}은(는) {appearance} 강아지예요. "
        f"{personality_phrase} 모습을 보여요(성격은 추정이에요). "
        "새로운 가족과 천천히 신뢰를 쌓아갈 친구랍니다."
    )

    note = (
        "이 결과는 AI가 만든 '초안'이에요. 실제 모습과 다를 수 있으니 "
        "보호소에서 외형·성격·소개글을 꼭 확인하고 수정한 뒤 저장해 주세요. "
        "AI는 강아지를 점수화하거나 입양을 단정하지 않아요."
    )

    return {
        "breed_label": breed,
        "breed_is_estimate": True,
        "color": color or None,
        "appearance": appearance,
        "intro": intro,
        "personality_keywords": keywords,
        "note": note,
    }


def journey_draft(memo: str, dog_name: str | None = None) -> dict:
    """입양자가 직접 쓴 메모를 '정리'해 글쓰기 초안을 돕습니다.

    원칙:
    - 행복/불행 같은 상태를 판단하지 않습니다.
    - 메모에 없는 사실이나 감정을 지어내지 않습니다(verbatim 유지).
    - 사용자의 문장을 다듬어 보기 좋게 정리하는 보조 역할만 합니다.
    """
    name = (dog_name or "우리 아이").strip() or "우리 아이"
    cleaned = " ".join((memo or "").split())  # 과도한 공백만 정리

    if not cleaned:
        draft = ""
    else:
        # 메모 내용은 그대로 두고, 부담 없는 머리말만 더합니다(감정 지어내지 않음).
        draft = f"{name}와 함께한 요즘이에요.\n\n{cleaned}"

    note = (
        "AI는 행복 여부를 판단하지 않아요. 직접 쓰신 메모의 표현만 다듬어 드렸어요. "
        "내용을 확인하고 자유롭게 고쳐서 올려주세요."
    )
    return {"draft": draft, "note": note}
