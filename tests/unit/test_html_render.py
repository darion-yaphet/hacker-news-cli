from hn_cli import render
from hn_cli.models import Comment


def _comment(content: str, author: str = "alice") -> Comment:
    return Comment(
        id="10",
        author=author,
        age="5m ago",
        content=content,
        parent_id="1",
    )


def test_render_comments_text_converts_html():
    comment = _comment("<p>Hello <b>World</b></p>")
    text = render.render_comments_text("1", [comment])

    assert "Hello" in text
    assert "World" in text
    assert "<p>" not in text


def test_render_comments_text_marks_deleted():
    comment = _comment("", author="unknown")
    text = render.render_comments_text("1", [comment])

    assert "[deleted]" in text


def test_render_comments_text_marks_empty():
    comment = _comment("")
    text = render.render_comments_text("1", [comment])

    assert "[empty]" in text
