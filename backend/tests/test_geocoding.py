"""카카오 지오코딩 어댑터 테스트 (파싱·stub·sync 연동)."""
from app.integrations import geocoding


def test_disabled_returns_none_without_key():
    # 키 미설정(stub) 상태에서는 조용히 None
    assert geocoding.is_enabled() is False
    assert geocoding.geocode("서울특별시 마포구 월드컵로 240") is None


def test_first_coord_maps_xy_to_latlng():
    payload = {"documents": [{"x": "126.901", "y": "37.566"}]}
    coord = geocoding._first_coord(payload)
    assert coord == (37.566, 126.901)  # (위도=y, 경도=x)


def test_first_coord_empty_returns_none():
    assert geocoding._first_coord({"documents": []}) is None
    assert geocoding._first_coord({}) is None


def test_geocode_uses_kakao(monkeypatch):
    # 키가 있는 것처럼 만들고 httpx 호출을 가짜 응답으로 대체
    monkeypatch.setattr(geocoding.settings, "KAKAO_REST_API_KEY", "test-key")

    class _Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"documents": [{"x": "127.0", "y": "37.5"}]}

    class _Client:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get(self, url, params=None):
            return _Resp()

    monkeypatch.setattr(geocoding.httpx, "Client", _Client)
    assert geocoding.geocode("서울특별시 마포구") == (37.5, 127.0)
