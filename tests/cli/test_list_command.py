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
    code = cli.run(
        ["list", "--feed", "top", "--limit", "1", "--page", "1", "--format", "json"],
        client=FakeClient(),
    )

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert code == 0
    assert payload["feed"] == "top"
    assert payload["page"] == 1
    assert payload["items"][0]["title"] == "Title"


def test_list_command_rejects_non_positive_limit(capsys):
    code = cli.run(["list", "--limit", "0"], client=FakeClient())

    err = capsys.readouterr().err
    assert code == 2
    assert "--limit" in err


def test_list_command_rejects_non_positive_page(capsys):
    code = cli.run(["list", "--page", "-1"], client=FakeClient())

    err = capsys.readouterr().err
    assert code == 2
    assert "--page" in err


def test_list_command_rejects_invalid_client_args(capsys):
    code = cli.run(["list", "--timeout", "0"], client=FakeClient())
    assert code == 2
    assert "--timeout" in capsys.readouterr().err

    code = cli.run(["list", "--retries", "-1"], client=FakeClient())
    assert code == 2
    assert "--retries" in capsys.readouterr().err

    code = cli.run(["list", "--backoff", "-0.5"], client=FakeClient())
    assert code == 2
    assert "--backoff" in capsys.readouterr().err
