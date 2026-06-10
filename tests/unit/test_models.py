import time

from hn_cli.models import Comment, Story, human_age


def test_human_age_buckets():
    now = int(time.time())
    assert human_age(None) == "unknown"
    assert human_age(now - 30).endswith("s ago")
    assert human_age(now - 300).endswith("m ago")
    assert human_age(now - 7200).endswith("h ago")
    assert human_age(now - 172800).endswith("d ago")


def test_story_from_api_maps_fields():
    data = {
        "id": 123,
        "title": "Example",
        "by": "alice",
        "score": 42,
        "time": 1_700_000_000,
        "url": "https://example.com",
        "descendants": 5,
    }

    story = Story.from_api(data, feed="top")

    assert story.id == "123"
    assert story.title == "Example"
    assert story.author == "alice"
    assert story.score == 42
    assert story.url == "https://example.com"
    assert story.comment_count == 5
    assert story.feed == "top"
    assert "ago" in story.age


def test_comment_from_api_handles_missing_fields():
    data = {
        "id": 99,
        "parent": 123,
        "time": 1_700_000_000,
        "text": None,
        "by": None,
    }

    comment = Comment.from_api(data)

    assert comment.id == "99"
    assert comment.parent_id == "123"
    assert comment.author == "unknown"
    assert comment.content == ""
    assert "ago" in comment.age
