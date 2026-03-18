from __future__ import annotations

import stat
import requests

from hn_cli import auth


def test_save_load_clear_auth(tmp_path, monkeypatch):
    auth_path = tmp_path / "auth.json"
    monkeypatch.setenv("HN_CLI_AUTH_FILE", str(auth_path))

    auth.save_auth(username="alice", cookies={"user": "alice"})
    loaded = auth.load_auth()
    assert loaded["username"] == "alice"
    assert loaded["cookies"]["user"] == "alice"
    mode = stat.S_IMODE(auth_path.stat().st_mode)
    assert mode == 0o600

    auth.clear_auth()
    assert auth.load_auth() == {}


def test_apply_auth_session_and_persist_roundtrip(tmp_path, monkeypatch):
    auth_path = tmp_path / "auth.json"
    monkeypatch.setenv("HN_CLI_AUTH_FILE", str(auth_path))

    session = requests.Session()
    session.cookies.set("a", "1")
    auth.persist_session(session=session, username="alice")

    restored = requests.Session()
    username = auth.apply_auth_session(restored)

    assert username == "alice"
    assert restored.cookies.get("a") == "1"
