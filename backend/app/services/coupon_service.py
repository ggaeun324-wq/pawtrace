"""쿠폰 서비스.

발급 정책(중요): 사람을 평가하지 않습니다. '꾸준한 반려생활 기록(Family Journey)'을
응원하는 혜택으로, 분기 기록 1건당 쿠폰 1장을 발급합니다.
journey_entry_id 로 멱등성을 보장해 같은 기록으로 중복 발급되지 않게 합니다.
"""
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain import CouponStatus
from app.models import Coupon, JourneyEntry, User

# 분기 기록 보상 쿠폰 금액(원). 운영에서는 설정/캠페인으로 분리 가능.
JOURNEY_REWARD_AMOUNT = 5000


def _new_code() -> str:
    return "PAW-" + secrets.token_hex(4).upper()


def issue_journey_reward(db: Session, user: User, entry: JourneyEntry) -> Coupon | None:
    """분기 기록 작성 보상 쿠폰을 발급합니다(기록당 1회, 멱등).

    이미 해당 기록으로 발급된 쿠폰이 있으면 새로 발급하지 않고 기존 것을 반환합니다.
    """
    existing = db.scalar(
        select(Coupon).where(Coupon.journey_entry_id == entry.id)
    )
    if existing is not None:
        return existing

    coupon = Coupon(
        user_id=user.id,
        code=_new_code(),
        amount=JOURNEY_REWARD_AMOUNT,
        status=CouponStatus.issued,
        source="journey_reward",
        journey_entry_id=entry.id,
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


def list_my_coupons(db: Session, user: User) -> list[Coupon]:
    return list(
        db.scalars(
            select(Coupon).where(Coupon.user_id == user.id).order_by(Coupon.id.desc())
        ).all()
    )
