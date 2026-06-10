from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import re
import time
from typing import Any, Callable, Iterable
from urllib.parse import unquote, urljoin

import requests

from .models import Comment, Story


class HNClientError(RuntimeError):
    pass


def _thread_order(comments: list[Comment], root_id: str) -> list[Comment]:
    """Reorder breadth-first fetched comments into thread (depth-first) order.

    Sibling order is preserved because the fetch appends comments in the
    parent's `kids` order.
    """
    children: dict[str, list[Comment]] = {}
    for comment in comments:
        children.setdefault(comment.parent_id, []).append(comment)

    ordered: list[Comment] = []
    stack = list(reversed(children.get(root_id, [])))
    while stack:
        comment = stack.pop()
        ordered.append(comment)
        stack.extend(reversed(children.get(comment.id, [])))
    return ordered


@dataclass
class HNClient:
    base_url: str = "https://hacker-news.firebaseio.com/v0"
    web_base_url: str = "https://news.ycombinator.com"
    timeout: float = 10.0
    max_retries: int = 2
    backoff: float = 0.5
    max_workers: int = 10
    sleep: Callable[[float], None] = time.sleep
    session: requests.Session | None = None

    FEED_MAP = {
        "top": "topstories",
        "new": "newstories",
        "best": "beststories",
        "ask": "askstories",
        "show": "showstories",
        "jobs": "jobstories",
    }

    def __post_init__(self) -> None:
        if self.session is None:
            self.session = requests.Session()

    @classmethod
    def feed_endpoint(cls, feed: str) -> str:
        if feed not in cls.FEED_MAP:
            raise ValueError(f"Unsupported feed: {feed}")
        return cls.FEED_MAP[feed]

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}/{path}.json"

    def _get_json(self, path: str) -> Any:
        if self.session is None:
            raise HNClientError("Session not initialized")
        last_exc: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.get(self._build_url(path), timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    delay = min(self.backoff * (2**attempt), 4.0)
                    if delay > 0:
                        self.sleep(delay)
        raise HNClientError("Request failed") from last_exc

    def _get_text(self, url: str) -> str:
        if self.session is None:
            raise HNClientError("Session not initialized")
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            raise HNClientError("Request failed") from exc

    def list_story_ids(self, feed: str) -> list[int]:
        endpoint = self.feed_endpoint(feed)
        data = self._get_json(endpoint)
        if not isinstance(data, list):
            raise HNClientError("Unexpected feed response")
        return [int(item) for item in data]

    def get_item(self, item_id: int | str) -> dict[str, Any]:
        data = self._get_json(f"item/{item_id}")
        if data is None:
            raise HNClientError(f"Item not found: {item_id}")
        if not isinstance(data, dict):
            raise HNClientError("Unexpected item response")
        return data

    def chunk_ids(self, ids: Iterable[int], limit: int, page: int) -> list[int]:
        start = max(0, (page - 1) * limit)
        end = start + limit
        return list(ids)[start:end]

    def list_stories(self, feed: str, limit: int, page: int) -> list[Story]:
        ids = self.list_story_ids(feed)
        selected = self.chunk_ids(ids, limit, page)
        if not selected:
            return []

        # Fetch concurrently; executor.map preserves input order and
        # re-raises any per-item error in order, matching serial behavior.
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            items = list(executor.map(self.get_item, selected))

        stories: list[Story] = []
        for data in items:
            if data.get("type") != "story":
                continue
            stories.append(Story.from_api(data, feed=feed))
        return stories

    def get_story(self, story_id: int | str) -> Story:
        data = self.get_item(story_id)
        if data.get("type") != "story":
            raise HNClientError("Item is not a story")
        return Story.from_api(data)

    def get_comments(
        self,
        story_id: int | str,
        max_depth: int | None = None,
        max_comments: int | None = None,
    ) -> list[Comment]:
        if max_depth is not None and max_depth < 1:
            raise ValueError("max_depth must be a positive integer")
        if max_comments is not None and max_comments < 1:
            raise ValueError("max_comments must be a positive integer")

        story = self.get_item(story_id)
        root_id = str(story.get("id", story_id))
        pending: list[tuple[int, int]] = [(cid, 0) for cid in story.get("kids", []) or []]
        if not pending:
            return []

        # Breadth-first so each level fetches concurrently; depth rides along
        # with each id so limits and rendering know how deep a comment sits.
        comments: list[Comment] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while pending:
                if max_comments is not None and len(comments) >= max_comments:
                    break
                futures = [(executor.submit(self.get_item, cid), depth) for cid, depth in pending]
                pending = []
                for future, depth in futures:
                    try:
                        data = future.result()
                    except HNClientError:
                        continue
                    if data.get("type") != "comment":
                        continue
                    comments.append(Comment.from_api(data, depth=depth))
                    if max_depth is None or depth + 1 < max_depth:
                        pending.extend((kid, depth + 1) for kid in data.get("kids", []) or [])

        if max_comments is not None:
            # Breadth-first order guarantees a parent precedes its children,
            # so truncating here never orphans a kept comment.
            comments = comments[:max_comments]
        return _thread_order(comments, root_id)

    def get_logged_in_user(self) -> str | None:
        html = self._get_text(f"{self.web_base_url}/news")
        match = re.search(r'href="user\?id=([^"&]+)".*?\|\s*<a href="logout\?', html, re.DOTALL)
        if not match:
            return None
        return unquote(match.group(1))

    def login(self, username: str, password: str) -> str:
        if self.session is None:
            raise HNClientError("Session not initialized")
        if not username.strip() or not password:
            raise HNClientError("Username and password are required")
        # Avoid stale cookies making a failed login appear successful.
        self.session.cookies.clear()
        try:
            response = self.session.post(
                f"{self.web_base_url}/login",
                data={"acct": username, "pw": password},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise HNClientError("Login request failed") from exc

        logged_in_user = self.get_logged_in_user()
        if not logged_in_user:
            raise HNClientError("Login failed: invalid username or password")
        return logged_in_user

    def logout(self) -> bool:
        if self.session is None:
            raise HNClientError("Session not initialized")
        html = self._get_text(f"{self.web_base_url}/news")
        match = re.search(r'href="(logout\?[^"]+)"', html)
        if not match:
            return False
        logout_url = urljoin(f"{self.web_base_url}/", unquote(match.group(1)))
        try:
            response = self.session.get(logout_url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise HNClientError("Logout request failed") from exc
        return True
