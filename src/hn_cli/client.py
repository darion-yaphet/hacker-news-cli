from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import logging
import re
import time
from typing import Any, Callable, Iterable
from urllib.parse import unquote, urljoin

import requests

from .models import Comment, Story


logger = logging.getLogger(__name__)

USER_AGENT = "hn-cli/0.1 (+https://github.com/darion-yaphet/hacker-news-cli)"

# HN has no auth API; login state is scraped from the web UI. These patterns
# are the single place to fix if news.ycombinator.com changes its markup.
_USER_LINK_RE = re.compile(r'href="user\?id=([^"&]+)".*?\|\s*<a href="logout\?', re.DOTALL)
_LOGOUT_LINK_RE = re.compile(r'href="(logout\?[^"]+)"')


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
        if isinstance(self.session, requests.Session):
            # Identify ourselves instead of the generic python-requests UA,
            # but never stomp a caller-provided custom User-Agent.
            current_agent = str(self.session.headers.get("User-Agent") or "")
            if not current_agent or current_agent.startswith("python-requests"):
                self.session.headers["User-Agent"] = USER_AGENT

    @classmethod
    def feed_endpoint(cls, feed: str) -> str:
        if feed not in cls.FEED_MAP:
            raise ValueError(f"Unsupported feed: {feed}")
        return cls.FEED_MAP[feed]

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}/{path}.json"

    def _request_with_retry(
        self, request: Callable[[], requests.Response], context: str
    ) -> requests.Response:
        attempts = self.max_retries + 1
        last_exc: Exception | None = None
        for attempt in range(attempts):
            try:
                response = request()
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    delay = min(self.backoff * (2**attempt), 4.0)
                    if delay > 0:
                        self.sleep(delay)
        raise HNClientError(
            f"{context} failed after {attempts} attempt(s): {last_exc}"
        ) from last_exc

    def _get_json(self, path: str) -> Any:
        session = self.session
        if session is None:
            raise HNClientError("Session not initialized")
        url = self._build_url(path)
        response = self._request_with_retry(
            lambda: session.get(url, timeout=self.timeout), f"GET {url}"
        )
        return response.json()

    def _get_text(self, url: str) -> str:
        session = self.session
        if session is None:
            raise HNClientError("Session not initialized")
        response = self._request_with_retry(
            lambda: session.get(url, timeout=self.timeout), f"GET {url}"
        )
        return response.text

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
        start = (page - 1) * limit
        return list(ids)[start : start + limit]

    def list_stories(self, feed: str, limit: int, page: int) -> list[Story]:
        if limit < 1:
            raise ValueError("limit must be a positive integer")
        if page < 1:
            raise ValueError("page must be a positive integer")
        ids = self.list_story_ids(feed)
        selected = self.chunk_ids(ids, limit, page)
        if not selected:
            return []

        # Fetch concurrently in feed order; a failed item is skipped with a
        # warning instead of failing the whole page — same policy as comments.
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [(executor.submit(self.get_item, sid), sid) for sid in selected]
            stories: list[Story] = []
            for future, sid in futures:
                try:
                    data = future.result()
                except HNClientError as exc:
                    logger.warning("Skipping story %s: %s", sid, exc)
                    continue
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
                futures = [
                    (executor.submit(self.get_item, cid), cid, depth) for cid, depth in pending
                ]
                pending = []
                for future, cid, depth in futures:
                    try:
                        data = future.result()
                    except HNClientError as exc:
                        logger.warning("Skipping comment %s: %s", cid, exc)
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
        match = _USER_LINK_RE.search(html)
        if not match:
            return None
        return unquote(match.group(1))

    def login(self, username: str, password: str) -> str:
        session = self.session
        if session is None:
            raise HNClientError("Session not initialized")
        if not username.strip() or not password:
            raise HNClientError("Username and password are required")
        # Avoid stale cookies making a failed login appear successful.
        session.cookies.clear()
        url = f"{self.web_base_url}/login"
        self._request_with_retry(
            lambda: session.post(
                url, data={"acct": username, "pw": password}, timeout=self.timeout
            ),
            f"Login POST {url}",
        )

        logged_in_user = self.get_logged_in_user()
        if not logged_in_user:
            raise HNClientError("Login failed: invalid username or password")
        return logged_in_user

    def logout(self) -> bool:
        session = self.session
        if session is None:
            raise HNClientError("Session not initialized")
        html = self._get_text(f"{self.web_base_url}/news")
        match = _LOGOUT_LINK_RE.search(html)
        if not match:
            return False
        logout_url = urljoin(f"{self.web_base_url}/", unquote(match.group(1)))
        self._request_with_retry(
            lambda: session.get(logout_url, timeout=self.timeout), f"Logout GET {logout_url}"
        )
        return True
