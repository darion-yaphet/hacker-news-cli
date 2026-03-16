import json

from hn_cli import cli


def test_run_without_args_returns_error(capsys):
    code = cli.run([])

    err = capsys.readouterr().err
    payload = json.loads(err)
    assert code == 2
    assert "error" in payload
