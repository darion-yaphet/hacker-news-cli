import json

from hn_cli import cli
from hn_cli.models import Comment


class FakeClient:
    def get_comments(
        self,
        story_id: str,
        max_depth: int | None = None,
        max_comments: int | None = None,
    ):
        assert story_id == "1"
        return [
            Comment(
                id="10",
                author="bob",
                age="5m ago",
                content="Hello",
                parent_id="1",
            )
        ]


def test_comments_command_outputs_json(capsys):
    code = cli.run(["comments", "--id", "1"], client=FakeClient())

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert code == 0
    assert payload["story_id"] == "1"
    assert payload["comments"][0]["id"] == "10"


def test_comments_command_passes_limits_to_client():
    captured: dict = {}

    class SpyClient:
        def get_comments(self, story_id, max_depth=None, max_comments=None):
            captured.update(story_id=story_id, max_depth=max_depth, max_comments=max_comments)
            return []

    code = cli.run(
        ["comments", "--id", "1", "--depth", "2", "--max-comments", "50"],
        client=SpyClient(),
    )

    assert code == 0
    assert captured == {"story_id": "1", "max_depth": 2, "max_comments": 50}


def test_comments_command_rejects_non_positive_depth(capsys):
    code = cli.run(["comments", "--id", "1", "--depth", "0"], client=FakeClient())

    err = capsys.readouterr().err
    assert code == 2
    assert "--depth" in err


def test_comments_command_rejects_non_positive_max_comments(capsys):
    code = cli.run(["comments", "--id", "1", "--max-comments", "-5"], client=FakeClient())

    err = capsys.readouterr().err
    assert code == 2
    assert "--max-comments" in err
