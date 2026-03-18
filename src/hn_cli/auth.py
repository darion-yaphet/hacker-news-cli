from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests


def auth_file_path() -> Path:
    configured = os.environ.get("HN_CLI_AUTH_FILE")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".config" / "hn-cli" / "auth.json"


def load_auth() -> dict[str, Any]:
    path = auth_file_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_auth(*, username: str, cookies: dict[str, str]) -> None:
    path = auth_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"username": username, "cookies": cookies}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    path.chmod(0o600)


def clear_auth() -> None:
    path = auth_file_path()
    if path.exists():
        path.unlink()


def apply_auth_session(session: requests.Session) -> str | None:
    data = load_auth()
    cookies = data.get("cookies")
    if isinstance(cookies, dict):
        session.cookies = requests.utils.cookiejar_from_dict(cookies)
    username = data.get("username")
    if isinstance(username, str) and username:
        return username
    return None


def persist_session(*, session: requests.Session, username: str) -> None:
    cookies = requests.utils.dict_from_cookiejar(session.cookies)
    save_auth(username=username, cookies=cookies)
