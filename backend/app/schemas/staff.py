"""보호소 직원(shelter_staff) 마이페이지 스키마.

- StaffAccount: 로그인한 직원 계정의 기본 정보.
- StaffShelter: 직원이 담당하는 보호소의 열람/수정 대상 정보.
- ShelterEditIn: 직원이 수정해서 DB 에 저장하는 보호소 정보(입력).
- StaffSummary: 직원 마이페이지 대시보드(보호소 + 운영 통계 + 계정).

원칙:
- 사람(직원/신청자)을 점수화하지 않습니다. 통계는 '운영 현황' 숫자일 뿐입니다.
- transparency_level 은 보호소의 '공개 정보 충분함'만 의미합니다(평가 아님).
"""
from pydantic import BaseModel, Field

from app.domain import TransparencyLevel, UserRole


class StaffAccount(BaseModel):
    id: int
    email: str
    display_name: str
    role: UserRole


class StaffShelter(BaseModel):
    id: int
    name: str
    region: str
    address: str | None = None
    phone: str | None = None
    description: str | None = None
    is_gov_registered: bool = False
    gov_reg_no: str | None = None
    transparency_level: TransparencyLevel


class ShelterEditIn(BaseModel):
    """직원이 담당 보호소에서 수정할 수 있는 필드(DB 저장).

    name/region 같은 식별 정보는 관리자 검증 영역이라 직원 수정 대상에서 제외합니다.
    """

    address: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=40)
    description: str | None = None
    is_gov_registered: bool | None = None
    gov_reg_no: str | None = Field(default=None, max_length=60)


class StaffStats(BaseModel):
    dog_count: int = 0            # 등록된 강아지 총수
    available_count: int = 0      # 입양 가능
    adopted_count: int = 0        # 입양 완료
    pending_applicants: int = 0   # 진행 중(종료/매칭완료 제외) 신청자 수


class StaffSummary(BaseModel):
    account: StaffAccount
    shelter: StaffShelter | None = None   # admin 이 담당 보호소 없이 접근하면 None 가능
    stats: StaffStats
