import json

from hn_cli import render


def test_print_json_outputs_valid_json(capsys):
    render.print_json({"ok": True})

    out = capsys.readouterr().out
    assert json.loads(out) == {"ok": True}


def test_print_error_outputs_json_to_stderr(capsys):
    render.print_error("failure", code=2)

    err = capsys.readouterr().err
    payload = json.loads(err)
    assert payload["error"]["message"] == "failure"
    assert payload["error"]["code"] == 2
