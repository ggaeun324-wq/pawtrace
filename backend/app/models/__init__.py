"""SQLAlchemy ORM 모델 (DB 스키마 정의).

설계 포인트:
- 강아지 점수/랭킹 컬럼 없음.
- shelters.transparency_level 은 '공개 정보 충분함'만 표현.
- source/external_id 로 공공데이터 vs 수동입력을 구분 → 멱등 동기화.
주의: 위치 컬럼은 PostGIS(geography Point, 4326)로 운영합니다.
"""
from datetime import date, datetime

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.domain import (
    AdoptionStatus,
    DataSource,
    PassportEventType,
    TransparencyLevel,
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
