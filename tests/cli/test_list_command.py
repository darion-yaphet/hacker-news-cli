import json

from hn_cli import cli
from hn_cli.models import Story


class FakeClient:
    def list_stories(self, feed: str, limit: int, page: int):
        assert feed == "top"
        assert limit == 1
        assert page == 1
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


def test_list_command_outputs_json(capsys):
    code = cli.run(["list", "--feed", "top", "--limit", "1", "--page", "1"], client=FakeClient())

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert code == 0
    assert payload["feed"] == "top"
    assert payload["page"] == 1
    assert payload["items"][0]["title"] == "Title"
