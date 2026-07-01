"""SQLAlchemy ORM 모델 (DB 스키마 정의).

설계 포인트:
- 강아지 점수/랭킹 컬럼 없음.
- shelters.transparency_level 은 '공개 정보 충분함'만 표현.
- source/external_id 로 공공데이터 vs 수동입력을 구분 → 멱등 동기화.
주의: 위치 컬럼은 PostGIS(geography Point, 4326)로 운영합니다.
"""
from datetime import date, datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.domain import (
    AdoptionStatus,
    ApplicationStatus,
    CouponStatus,
    DataSource,
    OrderStatus,
    PassportEventType,
    TransparencyLevel,
    UserRole,
)


class Shelter(Base):
    __tablename__ = "shelters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    region: Mapped[str] = mapped_column(String(40), index=True)
    address: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None]
    is_gov_registered: Mapped[bool] = mapped_column(Boolean, default=False)
    gov_reg_no: Mapped[str | None] = mapped_column(String(60))
    transparency_level: Mapped[TransparencyLevel] = mapped_column(
        default=TransparencyLevel.unverified
    )
    source: Mapped[DataSource] = mapped_column(default=DataSource.manual)
    external_id: Mapped[str | None] = mapped_column(String(80), index=True)
    phone: Mapped[str | None] = mapped_column(String(40))
    # 지도 표시용 좌표(스키마 lat/lng 와 1:1). 프론트 마커가 직접 사용합니다.
    lat: Mapped[float | None] = mapped_column(Float)
    lng: Mapped[float | None] = mapped_column(Float)
    # PostGIS 좌표. 반경검색(ST_DWithin, Sprint 2)을 위해 미리 컬럼만 둡니다.
    # spatial_index=False: 첫 마이그레이션을 단순하게 유지하고 인덱스는 검색 구현 시 추가.
    location: Mapped[object | None] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=False)
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    dogs: Mapped[list["Dog"]] = relationship(back_populates="shelter")


class Dog(Base):
    __tablename__ = "dogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    shelter_id: Mapped[int] = mapped_column(ForeignKey("shelters.id"))
    name: Mapped[str] = mapped_column(String(80))
    breed_label: Mapped[str | None] = mapped_column(String(80))
    # 품종은 보호견 특성상 대부분 추정. 스키마 breed_is_estimate 와 1:1.
    breed_is_estimate: Mapped[bool] = mapped_column(Boolean, default=True)
    age_estimate: Mapped[str | None] = mapped_column(String(40))
    gender: Mapped[str | None] = mapped_column(String(10))
    is_neutered: Mapped[bool | None]
    adoption_status: Mapped[AdoptionStatus] = mapped_column(
        default=AdoptionStatus.protected
    )
    # 보호 공고 마감일(임박 강아지 정렬용). 공공데이터 noticeEdt 와 1:1.
    # 마감 후에는 만나기 어려울 수 있어 '지금 가족이 필요한 아이들' 노출에 사용.
    protect_end_date: Mapped[date | None] = mapped_column(Date)
    source: Mapped[DataSource] = mapped_column(default=DataSource.manual)
    external_id: Mapped[str | None] = mapped_column(String(80), index=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(300))
    story: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    shelter: Mapped["Shelter"] = relationship(back_populates="dogs")
    events: Mapped[list["PassportEvent"]] = relationship(back_populates="dog")


class PassportEvent(Base):
    __tablename__ = "passport_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    dog_id: Mapped[int] = mapped_column(ForeignKey("dogs.id"))
    event_type: Mapped[PassportEventType]
    event_date: Mapped[date | None] = mapped_column(Date)
    title: Mapped[str] = mapped_column(String(120))
    memo: Mapped[str | None]
    source: Mapped[DataSource] = mapped_column(default=DataSource.manual)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    dog: Mapped["Dog"] = relationship(back_populates="events")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    target_type: Mapped[str] = mapped_column(String(20))
    target_id: Mapped[int]
    description: Mapped[str]
    image_url: Mapped[str | None] = mapped_column(String(300))
    reporter_contact: Mapped[str | None] = mapped_column(String(120))
    ai_category: Mapped[str | None] = mapped_column(String(60))  # P2: Bedrock 분류
    status: Mapped[str] = mapped_column(String(20), default="pending")
    admin_memo: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class User(Base):
    """회원 계정. 비밀번호는 평문 저장 금지 — bcrypt 해시만 저장합니다."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(60))
    role: Mapped[UserRole] = mapped_column(default=UserRole.user)
    # shelter_staff 인 경우 담당 보호소. 그 외에는 NULL.
    shelter_id: Mapped[int | None] = mapped_column(ForeignKey("shelters.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Adoption(Base):
    """입양 관계 — '누가 어떤 강아지를 입양했는가'.

    Family Journey(입양자만 작성)와 해피엔딩의 토대가 됩니다.
    입양 신청(AdoptionApplication)이 matched 되면 보호소가 이 레코드를 생성합니다.
    """

    __tablename__ = "adoptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    dog_id: Mapped[int] = mapped_column(ForeignKey("dogs.id"), index=True)
    adopted_at: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship()
    dog: Mapped["Dog"] = relationship()


class AdoptionApplication(Base):
    """입양 신청 — 사용자가 특정 강아지에 입양을 신청합니다.

    보호소 직원이 신청자 목록(Shelter Applicant Review)에서 확인합니다.
    status 는 '진행 단계'일 뿐, 사람을 합격/불합격으로 평가하지 않습니다.
    """

    __tablename__ = "adoption_applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    dog_id: Mapped[int] = mapped_column(ForeignKey("dogs.id"), index=True)
    status: Mapped[ApplicationStatus] = mapped_column(
        default=ApplicationStatus.submitted
    )
    message: Mapped[str | None]  # 신청자가 남긴 한마디(선택)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship()
    dog: Mapped["Dog"] = relationship()


class Course(Base):
    """PawTrace Academy 교육 과정.

    책임 있는 입양을 준비하도록 돕는 콘텐츠 + 퀴즈. 강아지를 추천하지 않습니다.
    """

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(120))
    emoji: Mapped[str | None] = mapped_column(String(8))
    summary: Mapped[str] = mapped_column(String(300))
    content: Mapped[str]  # 교육 본문(여러 단락)
    order_no: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    questions: Mapped[list["QuizQuestion"]] = relationship(
        back_populates="course", order_by="QuizQuestion.order_no"
    )


class QuizQuestion(Base):
    """교육 과정별 퀴즈 문항. 정답(answer_index)은 응답으로 노출하지 않습니다."""

    __tablename__ = "quiz_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), index=True)
    order_no: Mapped[int] = mapped_column(Integer, default=0)
    question: Mapped[str] = mapped_column(String(300))
    options: Mapped[list] = mapped_column(JSON)  # 보기 문자열 배열
    answer_index: Mapped[int] = mapped_column(Integer)
    explanation: Mapped[str | None] = mapped_column(String(400))

    course: Mapped["Course"] = relationship(back_populates="questions")


class AcademyCompletion(Base):
    """사용자별 교육 수료 기록(=수료 배지). (user, course) 당 1건."""

    __tablename__ = "academy_completions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), index=True)
    score: Mapped[int] = mapped_column(Integer)        # 맞은 개수
    total: Mapped[int] = mapped_column(Integer)        # 전체 문항 수
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship()
    course: Mapped["Course"] = relationship()


class UserProfile(Base):
    """사용자 입양 준비 프로필 (사용자 본인이 작성).

    민감 정보가 아니라 '입양 준비 활동'을 정리하는 용도입니다.
    보호소/관리자는 Trust Profile 형태로 열람하지만, 사람을 점수화하지 않습니다.
    """

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, index=True
    )
    housing_type: Mapped[str | None] = mapped_column(String(40))   # 주거 형태
    household: Mapped[str | None] = mapped_column(String(120))     # 함께 사는 사람
    experience: Mapped[str | None] = mapped_column(String(300))    # 반려 경험
    daily_hours: Mapped[str | None] = mapped_column(String(40))    # 함께할 수 있는 시간
    intro: Mapped[str | None]                                      # 자기소개/동기
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship()


class AdoptionChecklist(Base):
    """입양 준비 체크리스트 (사용자 본인이 체크).

    각 항목은 '준비 활동'일 뿐 합격/불합격 기준이 아닙니다.
    """

    __tablename__ = "adoption_checklists"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, index=True
    )
    vet_info: Mapped[bool] = mapped_column(Boolean, default=False)      # 동물병원 정보 확인
    budget_ready: Mapped[bool] = mapped_column(Boolean, default=False)  # 양육 비용 점검
    space_ready: Mapped[bool] = mapped_column(Boolean, default=False)   # 생활 공간 점검
    family_agreed: Mapped[bool] = mapped_column(Boolean, default=False) # 가족 동의
    time_committed: Mapped[bool] = mapped_column(Boolean, default=False) # 돌봄 시간 확보
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship()


class JourneyEntry(Base):
    """Family Journey — 입양자가 직접 남기는 분기별 반려생활 기록.

    철학: '입양은 끝이 아니라 시작'. 입양한 사용자만 작성할 수 있고,
    댓글은 없으며 '응원(cheer)'만 받을 수 있습니다.
    AI는 행복을 판단하지 않고, 사용자가 쓴 메모 정리만 돕습니다.
    """

    __tablename__ = "journey_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    dog_id: Mapped[int] = mapped_column(ForeignKey("dogs.id"), index=True)
    quarter_label: Mapped[str | None] = mapped_column(String(20))  # 예: "2026 2분기"
    title: Mapped[str] = mapped_column(String(120))
    body: Mapped[str]
    photo_url: Mapped[str | None] = mapped_column(String(300))
    cheers: Mapped[int] = mapped_column(Integer, default=0)  # 응원(좋아요) 수
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship()
    dog: Mapped["Dog"] = relationship()



class Product(Base):
    """쇼핑몰 상품 (굿즈/사료/후원 키트 등).

    MVP 범위: 상품 진열만 합니다(장바구니/결제 없음).
    PawTrace 미션에 맞춰 '수익 일부가 보호소를 후원한다'는 메시지를
    supports_shelter 플래그로 표현할 수 있게 두었습니다.
    """

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(40), index=True)  # 예: 사료/장난감/굿즈
    price: Mapped[int] = mapped_column(Integer)  # 원(KRW) 단위 정수
    image_url: Mapped[str | None] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(String(400))
    supports_shelter: Mapped[bool] = mapped_column(Boolean, default=False)  # 보호소 후원 상품
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # ── 커머스 확장 ──
    seller_id: Mapped[int | None] = mapped_column(ForeignKey("sellers.id"), index=True)
    stock: Mapped[int] = mapped_column(Integer, default=0, server_default="0")  # 재고 수량
    # 판매액 중 보호소 후원으로 적립되는 비율(%) — 미션(수익 일부 후원) 구현
    donation_rate: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    seller: Mapped["Seller | None"] = relationship()


class Seller(Base):
    """쇼핑몰 판매자 — 수제작가/소상공인.

    매출 일부(products.donation_rate)가 보호소 후원으로 이어지는 구조를 지원합니다.
    """

    __tablename__ = "sellers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    contact: Mapped[str | None] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Coupon(Base):
    """쿠폰 — 분기별 Family Journey 기록 작성 보상 등으로 발급.

    사람을 평가하지 않고, '꾸준한 반려생활 기록'을 응원하는 혜택입니다.
    journey_entry_id 로 '어떤 기록에 대한 보상인지'를 연결해 분기당 중복 발급을 막습니다.
    """

    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    amount: Mapped[int] = mapped_column(Integer)  # 할인 금액(원)
    status: Mapped[CouponStatus] = mapped_column(default=CouponStatus.issued)
    source: Mapped[str | None] = mapped_column(String(40))  # 예: journey_reward
    journey_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("journey_entries.id"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    used_at: Mapped[datetime | None] = mapped_column(DateTime)


class Order(Base):
    """주문 — 결제 트랜잭션(재고 차감 + 후원액 계산 + 쿠폰 사용)을 하나로 묶습니다.

    MVP 는 PG 연동 없이 status='paid' 로 확정합니다. 재고/쿠폰 정합성이 핵심이라
    부하테스트에서 '쓰기·동시성' 워크로드로 활용됩니다.
    """

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.paid)
    total_amount: Mapped[int] = mapped_column(Integer, default=0)     # 최종 결제액(쿠폰 적용 후)
    discount_amount: Mapped[int] = mapped_column(Integer, default=0)  # 쿠폰 할인액
    donation_amount: Mapped[int] = mapped_column(Integer, default=0)  # 보호소 후원 적립액
    coupon_id: Mapped[int | None] = mapped_column(ForeignKey("coupons.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    """주문 상세 — 상품별 수량/단가 스냅샷(주문 시점 가격 보존)."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[int] = mapped_column(Integer)  # 주문 시점 단가(원)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()


class Cart(Base):
    """장바구니 — 사용자당 1개(활성). 결제 전 임시 상태를 영속 저장합니다.

    DB 선택 이유(설계 결정):
    - 장바구니는 '결제 전 담아둔 상태'라 기기/세션이 바뀌어도 유지돼야 하므로
      영속 스토리지인 PostgreSQL 에 저장합니다(주문/재고와 같은 DB → 정합성·트랜잭션 용이).
    - Redis 는 이미 조회 캐시로 쓰고 있고, 초고트래픽에서 장바구니를 Redis 로 옮기는 것은
      '확장 카드'로 남겨둡니다(TTL 세션 장바구니). MVP 는 단순·정확을 우선합니다.
    """

    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True)
    # 사용자당 활성 장바구니 1개 → user_id 유니크
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    items: Mapped[list["CartItem"]] = relationship(
        back_populates="cart", cascade="all, delete-orphan"
    )


class CartItem(Base):
    """장바구니 담긴 항목 — (cart, product) 조합은 유일(수량으로 합산)."""

    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    cart: Mapped["Cart"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()
