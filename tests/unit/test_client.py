import pytest
import requests

from hn_cli.client import HNClient, HNClientError


def test_feed_endpoint_valid():
    assert HNClient.feed_endpoint("top") == "topstories"
    assert HNClient.feed_endpoint("new") == "newstories"


def test_feed_endpoint_invalid():
    with pytest.raises(ValueError):
        HNClient.feed_endpoint("unknown")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class DictSession:
    """Returns canned JSON responses keyed by URL suffix."""

    def __init__(self, items: dict):
        self._items = items  # item_id (str) -> dict
        self.calls: list[str] = []

    def get(self, url: str, timeout: float):
        self.calls.append(url)
        for key, value in self._items.items():
            if url.endswith(f"/{key}.json"):
                return FakeResponse(value)
        raise requests.RequestException(f"unexpected url: {url}")


# ---------------------------------------------------------------------------
# get_comments tests
# ---------------------------------------------------------------------------


def _make_story(kids: list[int]) -> dict:
    return {"id": 1, "type": "story", "by": "alice", "title": "T", "kids": kids}


def _make_comment(cid: int, parent: int, kids: list[int] | None = None) -> dict:
    return {
        "id": cid,
        "type": "comment",
        "by": "bob",
        "text": f"comment {cid}",
        "parent": parent,
        "kids": kids or [],
    }


def test_get_comments_empty():
    items = {"item/1": _make_story(kids=[])}
    client = HNClient(session=DictSession(items))
    assert client.get_comments(1) == []


def test_get_comments_flat():
    """Three sibling comments, no nesting."""
    items = {
        "item/1": _make_story(kids=[10, 11, 12]),
        "item/10": _make_comment(10, parent=1),
        "item/11": _make_comment(11, parent=1),
        "item/12": _make_comment(12, parent=1),
    }
    client = HNClient(session=DictSession(items))
    comments = client.get_comments(1)

    assert [c.id for c in comments] == ["10", "11", "12"]


def test_get_comments_nested():
    """Comment 10 has a reply (20), which has a reply (30)."""
    items = {
        "item/1": _make_story(kids=[10]),
        "item/10": _make_comment(10, parent=1, kids=[20]),
        "item/20": _make_comment(20, parent=10, kids=[30]),
        "item/30": _make_comment(30, parent=20),
    }
    client = HNClient(session=DictSession(items))
    comments = client.get_comments(1)

    assert [c.id for c in comments] == ["10", "20", "30"]


def test_get_comments_thread_order_and_depth():
    """Comments come back in thread (DFS) order with depth filled in."""
    items = {
        "item/1": _make_story(kids=[10, 11]),
        "item/10": _make_comment(10, parent=1, kids=[20]),
        "item/11": _make_comment(11, parent=1, kids=[21]),
        "item/20": _make_comment(20, parent=10),
        "item/21": _make_comment(21, parent=11),
    }
    client = HNClient(session=DictSession(items))
    comments = client.get_comments(1)

    assert [c.id for c in comments] == ["10", "20", "11", "21"]
    assert [c.depth for c in comments] == [0, 1, 0, 1]


def test_get_comments_max_depth_limits_descent():
    """max_depth=1 keeps only top-level comments and never fetches replies."""
    items = {
        "item/1": _make_story(kids=[10, 11]),
        "item/10": _make_comment(10, parent=1, kids=[20]),
        "item/11": _make_comment(11, parent=1, kids=[21]),
        "item/20": _make_comment(20, parent=10),
        "item/21": _make_comment(21, parent=11),
    }
    session = DictSession(items)
    client = HNClient(session=session)
    comments = client.get_comments(1, max_depth=1)

    assert [c.id for c in comments] == ["10", "11"]
    # story + 2 top-level comments only; replies never requested
    assert len(session.calls) == 3


def test_get_comments_max_comments_truncates():
    """max_comments caps the result, keeping parents before children."""
    items = {
        "item/1": _make_story(kids=[10, 11]),
        "item/10": _make_comment(10, parent=1, kids=[20]),
        "item/11": _make_comment(11, parent=1, kids=[21]),
        "item/20": _make_comment(20, parent=10),
        "item/21": _make_comment(21, parent=11),
    }
    client = HNClient(session=DictSession(items))
    comments = client.get_comments(1, max_comments=3)

    # breadth-first fill: both top-levels kept, then first reply, in thread order
    assert [c.id for c in comments] == ["10", "20", "11"]


def test_get_comments_rejects_non_positive_limits():
    client = HNClient(session=DictSession({"item/1": _make_story(kids=[])}))
    with pytest.raises(ValueError):
        client.get_comments(1, max_depth=0)
    with pytest.raises(ValueError):
        client.get_comments(1, max_comments=-1)


def test_get_comments_concurrent_fetches():
    """All siblings at a given depth must be fetched before their children."""
    items = {
        "item/1": _make_story(kids=[10, 11]),
        "item/10": _make_comment(10, parent=1, kids=[20]),
        "item/11": _make_comment(11, parent=1, kids=[21]),
        "item/20": _make_comment(20, parent=10),
        "item/21": _make_comment(21, parent=11),
    }
    session = DictSession(items)
    client = HNClient(session=session)
    comments = client.get_comments(1)

    assert {c.id for c in comments} == {"10", "11", "20", "21"}
    # story itself fetched once, then 2+2 comments = 5 total item fetches
    assert len(session.calls) == 5


def test_list_stories_preserves_order():
    """Concurrent fetching must still return stories in feed-id order."""
    items = {
        "topstories": [10, 11, 12],
        "item/10": {"id": 10, "type": "story", "by": "a", "title": "First"},
        "item/11": {"id": 11, "type": "story", "by": "b", "title": "Second"},
        "item/12": {"id": 12, "type": "story", "by": "c", "title": "Third"},
    }
    client = HNClient(session=DictSession(items))
    stories = client.list_stories("top", limit=30, page=1)

    assert [s.id for s in stories] == ["10", "11", "12"]
    assert [s.title for s in stories] == ["First", "Second", "Third"]


def test_list_stories_filters_non_story():
    """Items that are not stories (e.g. jobs/polls) are skipped, order kept."""
    items = {
        "topstories": [10, 11, 12],
        "item/10": {"id": 10, "type": "story", "by": "a", "title": "Keep"},
        "item/11": {"id": 11, "type": "job", "by": "b", "title": "Drop"},
        "item/12": {"id": 12, "type": "story", "by": "c", "title": "Keep2"},
    }
    client = HNClient(session=DictSession(items))
    stories = client.list_stories("top", limit=30, page=1)

    assert [s.id for s in stories] == ["10", "12"]


def test_list_stories_empty_page():
    items = {"topstories": [10, 11]}
    client = HNClient(session=DictSession(items))
    assert client.list_stories("top", limit=10, page=5) == []


def test_get_comments_skips_failed_item_with_warning(caplog):
    """A failing item fetch is skipped but reported, never silently dropped."""

    class FlakySession:
        def get(self, url: str, timeout: float):
            if url.endswith("/item/11.json"):
                raise requests.RequestException("timeout")
            payload = {
                "item/1": _make_story(kids=[10, 11, 12]),
                "item/10": _make_comment(10, parent=1),
                "item/12": _make_comment(12, parent=1),
            }
            for key, value in payload.items():
                if url.endswith(f"/{key}.json"):
                    return FakeResponse(value)
            raise requests.RequestException(f"unexpected: {url}")

    client = HNClient(session=FlakySession(), backoff=0, sleep=lambda _: None)
    with caplog.at_level("WARNING", logger="hn_cli.client"):
        comments = client.get_comments(1)

    assert [c.id for c in comments] == ["10", "12"]
    assert "11" in caplog.text


def test_list_stories_rejects_non_positive_limit_page():
    client = HNClient(session=DictSession({"topstories": [10]}))
    with pytest.raises(ValueError):
        client.list_stories("top", limit=0, page=1)
    with pytest.raises(ValueError):
        client.list_stories("top", limit=10, page=0)


def test_get_json_error_includes_url_and_attempts():
    """Network failures must surface the URL and attempt count, not a bare message."""

    class DeadSession:
        def get(self, url: str, timeout: float):
            raise requests.RequestException("connection refused")

    client = HNClient(session=DeadSession(), max_retries=1, backoff=0, sleep=lambda _: None)
    with pytest.raises(HNClientError) as excinfo:
        client.get_item(42)

    message = str(excinfo.value)
    assert "item/42.json" in message
    assert "2 attempt" in message
    assert "connection refused" in message
