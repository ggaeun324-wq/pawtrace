"""사용자 저장소 (DB 백엔드)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain import UserRole
from app.models import User


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalars(select(User).where(User.email == email)).first()


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def create(
    db: Session,
    *,
    email: str,
    hashed_password: str,
    display_name: str,
    role: UserRole,
    shelter_id: int | None,
) -> User:
    user = User(
        email=email,
        hashed_password=hashed_password,
        display_name=display_name,
        role=role,
        shelter_id=shelter_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
