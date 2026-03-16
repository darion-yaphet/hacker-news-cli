import json

from hn_cli import cli
from hn_cli.models import Story


class FakeClient:
    def get_story(self, story_id: str):
        assert story_id == "1"
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


def test_link_command_outputs_json(capsys):
    code = cli.run(["link", "--id", "1"], client=FakeClient())

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert code == 0
    assert payload == {"id": "1", "url": "https://example.com"}
