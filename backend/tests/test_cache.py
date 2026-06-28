"""Redis 캐시 테스트 (fail-open 동작 + cache-aside 흐름).

실제 Redis 없이도 통과하도록 설계했습니다:
- fail-open: 클라이언트가 None/예외여도 안전하게 동작.
- cache-aside: 캐시 함수를 인메모리 가짜로 대체해 흐름만 검증.
"""
from app.core import cache
from app.services import dog_service


def test_get_json_returns_none_when_no_client(monkeypatch):
    # 클라이언트가 없으면(Redis 미연결) 미스처럼 None
    monkeypatch.setattr(cache, "get_client", lambda: None)
    assert cache.get_json("any-key") is None
    # set/delete 도 예외 없이 무시되어야 함
    cache.set_json("any-key", {"a": 1}, 10)
    cache.delete("any-key")


def test_ping_false_when_no_client(monkeypatch):
    monkeypatch.setattr(cache, "get_client", lambda: None)
    assert cache.ping() is False


def test_get_json_fail_open_on_error(monkeypatch):
    # 클라이언트가 있어도 get 이 터지면 None 으로 폴백(요청은 살아있음)
    class _Boom:
        def get(self, key):
            raise cache.RedisError("down")

    monkeypatch.setattr(cache, "get_client", lambda: _Boom())
    assert cache.get_json("k") is None


def test_urgent_dogs_uses_cache_aside(monkeypatch):
    """첫 호출은 DB→캐시 저장, 두 번째 호출은 캐시 히트(DB 미조회)."""
    store: dict = {}
    monkeypatch.setattr(cache, "get_json", lambda k: store.get(k))
    monkeypatch.setattr(cache, "set_json", lambda k, v, ttl: store.__setitem__(k, v))

    calls = {"db": 0}
    sample = [
        {
            "id": 1,
            "name": "봄이",
            "adoption_status": "available",
            "shelter_id": 1,
            "shelter_name": "행복보호소",
            "story": "가족을 기다려요",
            "protect_end_date": None,
        }
    ]

    def fake_repo(db):
        calls["db"] += 1
        return list(sample)

    monkeypatch.setattr(dog_service.repo, "get_urgent_dogs", fake_repo)

    first = dog_service.get_urgent_dogs(db=None)
    second = dog_service.get_urgent_dogs(db=None)

    assert calls["db"] == 1            # DB 는 한 번만 조회
    assert len(first) == len(second) == 1
    assert first[0].name == "봄이"
