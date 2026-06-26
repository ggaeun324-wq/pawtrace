"""강아지 / Pet Passport 라우트.

- GET /dogs/today         홈 '오늘의 친구'
- GET /dogs/{id}/passport 생애 타임라인
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dog import DogPassport, DogToday
from app.services import dog_service

router = APIRouter()


@router.get("/today", response_model=DogToday)
def today_dog(db: Annotated[Session, Depends(get_db)]):
    dog = dog_service.get_today_dog(db)
    if not dog:
        raise HTTPException(status_code=404, detail="오늘의 친구가 아직 없어요")
    return dog


@router.get("/{dog_id}/passport", response_model=DogPassport)
def dog_passport(dog_id: int, db: Annotated[Session, Depends(get_db)]):
    passport = dog_service.get_passport(db, dog_id)
    if not passport:
        raise HTTPException(status_code=404, detail="강아지를 찾을 수 없어요")
    return passport
