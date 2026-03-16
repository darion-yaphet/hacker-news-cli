import requests

from hn_cli.client import HNClient


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class FlakySession:
    def __init__(self, fail_times: int):
        self.fail_times = fail_times
        self.attempts = 0

    def get(self, url, timeout):
        self.attempts += 1
        if self.attempts <= self.fail_times:
            raise requests.RequestException("boom")
        return FakeResponse({"ok": True})


def test_backoff_uses_exponential_delays():
    sleeps = []

    def fake_sleep(duration: float) -> None:
        sleeps.append(duration)

    client = HNClient(
        session=FlakySession(fail_times=2),
        max_retries=2,
        backoff=0.5,
        sleep=fake_sleep,
    )

    data = client._get_json("item/1")

    assert data == {"ok": True}
    assert sleeps == [0.5, 1.0]


def test_backoff_caps_delay():
    sleeps = []

    def fake_sleep(duration: float) -> None:
        sleeps.append(duration)

    client = HNClient(
        session=FlakySession(fail_times=3),
        max_retries=3,
        backoff=3.0,
        sleep=fake_sleep,
    )

    data = client._get_json("item/1")

    assert data == {"ok": True}
    assert sleeps == [3.0, 4.0, 4.0]
