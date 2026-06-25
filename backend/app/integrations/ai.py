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
