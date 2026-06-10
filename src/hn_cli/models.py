from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any


def human_age(timestamp: int | None) -> str:
    if timestamp is None:
        return "unknown"

    now = int(time.time())
    delta = max(0, now - int(timestamp))
    if delta < 60:
        return f"{delta}s ago"
    if delta < 3600:
        return f"{delta // 60}m ago"
    if delta < 86400:
        return f"{delta // 3600}h ago"
    return f"{delta // 86400}d ago"


@dataclass(frozen=True)
class Story:
    id: str
    title: str
    author: str
    score: int
    age: str
    url: str
    comment_count: int
    feed: str | None = None

    @classmethod
    def from_api(cls, data: dict[str, Any], feed: str | None = None) -> "Story":
        return cls(
            id=str(data.get("id", "")),
            title=data.get("title") or "",
            author=data.get("by") or "unknown",
            score=int(data.get("score") or 0),
            age=human_age(data.get("time")),
            url=data.get("url") or "",
            comment_count=int(data.get("descendants") or 0),
            feed=feed,
        )


@dataclass(frozen=True)
class Comment:
    id: str
    author: str
    age: str
    content: str
    parent_id: str
    depth: int = 0

    @classmethod
    def from_api(cls, data: dict[str, Any], depth: int = 0) -> "Comment":
        return cls(
            id=str(data.get("id", "")),
            author=data.get("by") or "unknown",
            age=human_age(data.get("time")),
            content=data.get("text") or "",
            parent_id=str(data.get("parent", "")),
            depth=depth,
        )


@dataclass(frozen=True)
class Feed:
    name: str
    display_label: str
