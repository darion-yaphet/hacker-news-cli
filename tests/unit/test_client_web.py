"""Tests for the web-scraping side of HNClient: login, logout, whoami."""

import pytest
import requests

from hn_cli.client import HNClient, HNClientError

LOGGED_IN_HTML = (
    '<a href="user?id=alice">alice</a> |\n<a href="logout?auth=abc&goto=news">logout</a>'
)
LOGGED_OUT_HTML = '<a href="login?goto=news">login</a>'


class FakeTextResponse:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self):
        pass


class FakeWebSession:
    """Canned session for news.ycombinator.com endpoints."""

    def __init__(self, html: str, post_fails: bool = False):
        self.html = html
        self.post_fails = post_fails
        self.cookies = requests.cookies.RequestsCookieJar()
        self.post_calls: list[dict] = []
        self.get_calls: list[str] = []

    def get(self, url: str, timeout: float):
        self.get_calls.append(url)
        return FakeTextResponse(self.html)

    def post(self, url: str, data: dict, timeout: float):
        self.post_calls.append(data)
        if self.post_fails:
            raise requests.RequestException("connection reset")
        return FakeTextResponse("")


def test_get_logged_in_user_parses_username():
    client = HNClient(session=FakeWebSession(LOGGED_IN_HTML))
    assert client.get_logged_in_user() == "alice"


def test_get_logged_in_user_returns_none_when_logged_out():
    client = HNClient(session=FakeWebSession(LOGGED_OUT_HTML))
    assert client.get_logged_in_user() is None


def test_login_success_returns_username():
    session = FakeWebSession(LOGGED_IN_HTML)
    client = HNClient(session=session)

    assert client.login("alice", "secret") == "alice"
    assert session.post_calls == [{"acct": "alice", "pw": "secret"}]


def test_login_rejects_blank_credentials():
    client = HNClient(session=FakeWebSession(LOGGED_IN_HTML))
    with pytest.raises(HNClientError):
        client.login("   ", "secret")
    with pytest.raises(HNClientError):
        client.login("alice", "")


def test_login_failure_when_not_logged_in_after_post():
    client = HNClient(session=FakeWebSession(LOGGED_OUT_HTML))
    with pytest.raises(HNClientError, match="invalid username or password"):
        client.login("alice", "wrong")


def test_login_request_error_includes_context():
    client = HNClient(session=FakeWebSession(LOGGED_IN_HTML, post_fails=True), max_retries=0)
    with pytest.raises(HNClientError, match="connection reset"):
        client.login("alice", "secret")


def test_logout_follows_logout_link():
    session = FakeWebSession(LOGGED_IN_HTML)
    client = HNClient(session=session)

    assert client.logout() is True
    assert any("logout?auth=abc" in url for url in session.get_calls)


def test_logout_returns_false_when_not_logged_in():
    client = HNClient(session=FakeWebSession(LOGGED_OUT_HTML))
    assert client.logout() is False


def test_get_text_error_includes_url():
    class DeadSession:
        def get(self, url: str, timeout: float):
            raise requests.RequestException("boom")

    client = HNClient(session=DeadSession(), max_retries=0)
    with pytest.raises(HNClientError) as excinfo:
        client.get_logged_in_user()

    message = str(excinfo.value)
    assert "news.ycombinator.com" in message
    assert "boom" in message


def test_get_text_retries_transient_failure():
    """Web requests get the same retry treatment as API requests."""

    class FlakyTextSession:
        def __init__(self):
            self.calls = 0

        def get(self, url: str, timeout: float):
            self.calls += 1
            if self.calls == 1:
                raise requests.RequestException("flaky")
            return FakeTextResponse(LOGGED_IN_HTML)

    session = FlakyTextSession()
    client = HNClient(session=session, backoff=0, sleep=lambda _: None)

    assert client.get_logged_in_user() == "alice"
    assert session.calls == 2


def test_default_session_sets_user_agent():
    client = HNClient()
    assert client.session is not None
    assert "hn-cli" in client.session.headers["User-Agent"]


def test_get_story_rejects_non_story():
    class ItemSession:
        def get(self, url: str, timeout: float):
            class R:
                def raise_for_status(self):
                    pass

                def json(self):
                    return {"id": 5, "type": "comment"}

            return R()

    client = HNClient(session=ItemSession())
    with pytest.raises(HNClientError, match="not a story"):
        client.get_story(5)
