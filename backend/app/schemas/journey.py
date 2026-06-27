"""Family Journey 스키마 (입양자의 분기별 반려생활 기록).

원칙: 입양한 사용자만 작성, 댓글 없음, 응원(cheer)만, AI는 메모 정리만.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JourneyDraftIn(BaseModel):
    memo: str = Field(min_length=1, max_length=2000)
    dog_name: str | None = None


class JourneyDraftOut(BaseModel):
    draft: str
    note: str


class JourneyIn(BaseModel):
    dog_id: int
    quarter_label: str | None = Field(default=None, max_length=20)
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1)
    photo_url: str | None = Field(default=None, max_length=300)


class JourneyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    author_name: str
    dog_id: int
    dog_name: str
    quarter_label: str | None
    title: str
    body: str
    photo_url: str | None
    cheers: int
    created_at: datetime


class CheerOut(BaseModel):
    id: int
    cheers: int
