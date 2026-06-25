"""객체 스토리지(Amazon S3) 연동 (stub).

신고/강아지 이미지를 S3에 저장하고, CloudFront(OAC)로 제공합니다.
실제 구현은 boto3 put_object / presigned URL 을 사용합니다.
"""
from app.core.config import settings


def upload_image(key: str, data: bytes) -> str:
    if not settings.AWS_S3_BUCKET:
        return f"local://stub/{key}"
    raise NotImplementedError("S3 업로드는 P1 후반에 구현합니다.")
