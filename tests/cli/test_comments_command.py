import json

from hn_cli import cli
from hn_cli.models import Comment


class FakeClient:
    def get_comments(self, story_id: str):
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
