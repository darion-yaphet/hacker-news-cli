from hn_cli.models import Comment, Story
from hn_cli.output import (
    comments_output,
    link_output,
    story_detail_output,
    story_list_output,
)


def _story():
    return Story(
        id="1",
        title="Title",
        author="alice",
        score=10,
        age="1h ago",
        url="https://example.com",
        comment_count=2,
        feed="top",
    )


def _comment():
    return Comment(
        id="10",
        author="bob",
        age="5m ago",
        content="Hello",
        parent_id="1",
    )


def test_story_list_output_contains_required_keys():
    data = story_list_output("top", 1, [_story()])

    assert data["feed"] == "top"
    assert data["page"] == 1
    item = data["items"][0]
    assert set(item.keys()) == {
        "id",
        "title",
        "author",
        "score",
        "age",
        "comment_count",
        "url",
    }


def test_story_detail_output_contains_required_keys():
    data = story_detail_output(_story())

    assert set(data.keys()) == {
        "id",
        "title",
        "author",
        "score",
        "age",
        "url",
        "comment_count",
    }


def test_comments_output_contains_required_keys():
    data = comments_output("1", [_comment()])

    assert data["story_id"] == "1"
    comment = data["comments"][0]
    assert set(comment.keys()) == {
        "id",
        "author",
        "age",
        "content",
        "parent_id",
        "depth",
    }
    assert comment["depth"] == 0


def test_link_output_contains_required_keys():
    data = link_output(_story())

    assert data == {"id": "1", "url": "https://example.com"}
