import json
import pytest

from hn_cli import cli
from hn_cli.models import Story


class FakeClient:
    def list_stories(self, feed: str, limit: int, page: int):
        return [
            Story(
                id="1",
                title="Title",
                author="alice",
                score=10,
                age="1h ago",
                url="https://example.com",
                comment_count=2,
                feed=feed,
            )
        ]


def test_default_format_is_text(capsys):
    code = cli.run(["list", "--feed", "top", "--limit", "1", "--page", "1"], client=FakeClient())

    out = capsys.readouterr().out
    assert code == 0
    assert "Title" in out
    with pytest.raises(json.JSONDecodeError):
        json.loads(out)


def test_format_json_outputs_json(capsys):
    code = cli.run(
        ["list", "--feed", "top", "--limit", "1", "--page", "1", "--format", "json"],
        client=FakeClient(),
    )

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert code == 0
    assert payload["feed"] == "top"
