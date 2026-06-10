from hn_cli import render
from hn_cli.models import Comment, Story


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


def test_render_list_text_contains_fields():
    text = render.render_list_text("top", 1, [_story()])
    assert "Title" in text
    assert "alice" in text


def test_render_story_text_contains_fields():
    text = render.render_story_text(_story())
    assert "Title" in text
    assert "https://example.com" in text


def test_render_comments_text_contains_fields():
    text = render.render_comments_text("1", [_comment()])
    assert "bob" in text
    assert "Hello" in text


def test_render_comments_text_indents_by_depth():
    top = Comment(id="10", author="bob", age="5m ago", content="parent", parent_id="1")
    reply = Comment(id="20", author="eve", age="1m ago", content="reply", parent_id="10", depth=1)
    text = render.render_comments_text("1", [top, reply])

    lines = text.splitlines()
    assert "- bob · 5m ago" in lines
    assert "  - eve · 1m ago" in lines
    assert "    reply" in lines


def test_render_link_text_contains_url():
    text = render.render_link_text(_story())
    assert "https://example.com" in text
