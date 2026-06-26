"""도메인 열거형(enum) 정의.

설계 원칙: 강아지를 점수화·랭킹하지 않습니다.
'투명성'은 보호소의 '공개 정보 충분함'에만 적용됩니다.
"""
from enum import Enum


class AdoptionStatus(str, Enum):
    protected = "protected"   # 보호중
    available = "available"   # 입양 가능
    reserved = "reserved"     # 예약됨
    adopted = "adopted"       # 입양 완료


class TransparencyLevel(str, Enum):
    unverified = "unverified"  # 정보 부족 (의심이 아님)
    basic = "basic"            # 기본 정보 확인
    verified = "verified"      # 공공데이터 일치 확인


class PassportEventType(str, Enum):
    rescue = "rescue"
    intake = "intake"
    medical = "medical"
    vaccination = "vaccination"
    neuter = "neuter"
    available = "available"
    adopted = "adopted"
    post_adoption = "post_adoption"


class DataSource(str, Enum):
    public_api = "public_api"  # 공공데이터 출처
    manual = "manual"          # 보호소/관리자 직접 입력


class UserRole(str, Enum):
    """회원 역할.
    - user: 일반 사용자(입양 희망자). 신고 등록 가능.
    - shelter_staff: 보호소 직원. 자기 보호소의 강아지/정보 관리.
    - admin: 플랫폼 관리자. 전체 검토/신뢰도 관리.
    """
    user = "user"
    shelter_staff = "shelter_staff"
    admin = "admin"
