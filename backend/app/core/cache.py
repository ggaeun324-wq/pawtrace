"""Redis 캐시 클라이언트 (cache-aside 패턴용).

설계 원칙(중요):
- **Fail-open(장애 시 개방)**: Redis 가 죽거나 느려도 절대 API 를 멈추지 않습니다.
  모든 캐시 작업은 예외를 흡수하고 캐시 미스처럼 동작 → 호출부는 DB 로 폴백합니다.
- **짧은 타임아웃**: 캐시가 느릴 때 요청 지연을 막기 위해 연결/응답 타임아웃을 짧게 둡니다.
- **지연 초기화(lazy singleton)**: 첫 사용 시 한 번만 클라이언트를 만들고 재사용합니다.

왜 캐시를 쓰나(포트폴리오 관점):
- '오늘의 공고(/dogs/urgent)'는 홈에서 가장 자주 호출되는 읽기 위주 엔드포인트입니다.
- 결과는 자주 바뀌지 않으므로(공공데이터 동기화/일자 변경 시에만) 짧은 TTL 캐싱으로
  DB 부하와 응답시간을 줄이는 전형적인 read-through 캐시 대상입니다.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import redis
from redis.exceptions import RedisError

from app.core.config import settings

logger = logging.getLogger(__name__)

# 캐시 키 네임스페이스 + TTL(초). 짧게 두고, 데이터 변경 시 명시적으로 무효화합니다.
URGENT_DOGS_KEY = "pawtrace:dogs:urgent"
URGENT_DOGS_TTL = 60

_client: redis.Redis | None = None
_init_failed = False


def get_client() -> redis.Redis | None:
    """Redis 클라이언트 싱글톤. 초기화 실패 시 None(캐시 비활성)으로 폴백."""
    global _client, _init_failed
    if _client is not None or _init_failed:
        return _client
    try:
        _client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=0.5,  # 연결이 느리면 빠르게 포기(요청 지연 방지)
            socket_timeout=0.5,
        )
    except (RedisError, ValueError) as exc:  # URL 오류 등
        _init_failed = True
        logger.warning("Redis 초기화 실패 — 캐시 없이 동작합니다: %s", exc)
        _client = None
    return _client


def ping() -> bool:
    """Redis 연결 가능 여부(헬스체크용). 실패 시 False."""
    client = get_client()
    if client is None:
        return False
    try:
        return bool(client.ping())
    except RedisError:
        return False


def get_json(key: str) -> Any | None:
    """캐시에서 JSON 값을 읽습니다. 미스/장애 시 None."""
    client = get_client()
    if client is None:
        return None
    try:
        raw = client.get(key)
    except RedisError as exc:
        logger.debug("cache get 실패(%s): %s", key, exc)
        return None
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return None


def set_json(key: str, value: Any, ttl: int) -> None:
    """JSON 직렬화하여 TTL 과 함께 저장합니다. 장애 시 조용히 무시."""
    client = get_client()
    if client is None:
        return
    try:
        client.set(key, json.dumps(value, ensure_ascii=False), ex=ttl)
    except (RedisError, TypeError) as exc:
        logger.debug("cache set 실패(%s): %s", key, exc)


def delete(*keys: str) -> None:
    """키를 삭제(무효화)합니다. 장애 시 조용히 무시."""
    if not keys:
        return
    client = get_client()
    if client is None:
        return
    try:
        client.delete(*keys)
    except RedisError as exc:
        logger.debug("cache delete 실패(%s): %s", keys, exc)
