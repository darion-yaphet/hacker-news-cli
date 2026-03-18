import json

from hn_cli import cli


class _DummySession:
    pass


class _LoginClient:
    def __init__(self) -> None:
        self.session = _DummySession()
        self.logged_in: tuple[str, str] | None = None

    def login(self, username: str, password: str) -> str:
        self.logged_in = (username, password)
        return username


def test_login_command_outputs_user_and_persists_session(capsys, monkeypatch):
    saved: dict[str, object] = {}

    def fake_apply_auth_session(_: object) -> None:
        return None

    def fake_persist_session(*, session: object, username: str) -> None:
        saved["session"] = session
        saved["username"] = username

    monkeypatch.setattr(cli, "apply_auth_session", fake_apply_auth_session)
    monkeypatch.setattr(cli, "persist_session", fake_persist_session)

    client = _LoginClient()
    code = cli.run(["login", "--username", "alice", "--password", "secret"], client=client)

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert code == 0
    assert payload == {"ok": True, "username": "alice"}
    assert client.logged_in == ("alice", "secret")
    assert saved["session"] is client.session
    assert saved["username"] == "alice"


class _IdentityClient:
    def __init__(self, user: str | None, logged_out: bool = True) -> None:
        self.session = _DummySession()
        self.user = user
        self.logged_out = logged_out

    def get_logged_in_user(self) -> str | None:
        return self.user

    def logout(self) -> bool:
        return self.logged_out


def test_whoami_command_reports_authenticated_state(capsys, monkeypatch):
    monkeypatch.setattr(cli, "apply_auth_session", lambda _: None)
    code = cli.run(["whoami"], client=_IdentityClient("alice"))

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert code == 0
    assert payload == {"authenticated": True, "username": "alice"}


def test_logout_command_clears_auth_and_returns_status(capsys, monkeypatch):
    called = {"clear": 0}
    monkeypatch.setattr(cli, "apply_auth_session", lambda _: None)
    monkeypatch.setattr(cli, "clear_auth", lambda: called.__setitem__("clear", called["clear"] + 1))

    code = cli.run(["logout"], client=_IdentityClient(None, logged_out=True))

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert code == 0
    assert payload == {"ok": True, "logged_out": True, "local_cleared": True}
    assert called["clear"] == 1


def test_logout_clears_local_auth_even_when_remote_fails(capsys, monkeypatch):
    class _FailingLogoutClient(_IdentityClient):
        def logout(self) -> bool:  # type: ignore[override]
            raise cli.HNClientError("network error")

    called = {"clear": 0}
    monkeypatch.setattr(cli, "apply_auth_session", lambda _: None)
    monkeypatch.setattr(cli, "clear_auth", lambda: called.__setitem__("clear", called["clear"] + 1))

    code = cli.run(["logout"], client=_FailingLogoutClient(None))

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert code == 0
    assert payload == {"ok": True, "logged_out": False, "local_cleared": True}
    assert called["clear"] == 1
