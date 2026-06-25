"""SQLAlchemy ORM 모델 (DB 스키마 정의).

설계 포인트:
- 강아지 점수/랭킹 컬럼 없음.
- shelters.transparency_level 은 '공개 정보 충분함'만 표현.
- source/external_id 로 공공데이터 vs 수동입력을 구분 → 멱등 동기화.
주의: 위치 컬럼은 PostGIS(geography Point, 4326)로 운영합니다.
"""
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, func
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
    # location: geography(Point,4326)  # PostGIS — geoalchemy2 Geometry 로 운영 추가
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    dogs: Mapped[list["Dog"]] = relationship(back_populates="shelter")


class Dog(Base):
    __tablename__ = "dogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    shelter_id: Mapped[int] = mapped_column(ForeignKey("shelters.id"))
    name: Mapped[str] = mapped_column(String(80))
    breed_label: Mapped[str | None] = mapped_column(String(80))
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
