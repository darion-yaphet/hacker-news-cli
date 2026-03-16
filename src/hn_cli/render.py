from __future__ import annotations

import sys
import html
import re
from typing import Any, Iterable, TextIO

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import html2text

from .models import Comment, Story


def _console() -> Console:
    return Console(record=True, force_terminal=False, color_system=None, no_color=True)


def print_json(payload: Any, stream: TextIO = sys.stdout) -> None:
    console = _console()
    console.print_json(data=payload)
    stream.write(console.export_text())


def print_text(text: str, stream: TextIO = sys.stdout) -> None:
    console = _console()
    console.print(text)
    stream.write(console.export_text())


def print_error(message: str, code: int = 1, details: dict | None = None) -> None:
    error = {"message": message, "code": code}
    if details:
        error["details"] = details
    print_json({"error": error}, stream=sys.stderr)


def render_list_text(feed: str, page: int, stories: Iterable[Story]) -> str:
    table = Table(title=f"Feed: {feed} (page {page})")
    table.add_column("#", justify="right")
    table.add_column("Title")
    table.add_column("Score", justify="right")
    table.add_column("By")
    table.add_column("Age")
    table.add_column("Comments", justify="right")
    table.add_column("URL")

    for index, story in enumerate(stories, start=1):
        table.add_row(
            str(index),
            story.title,
            str(story.score),
            story.author,
            story.age,
            str(story.comment_count),
            story.url,
        )

    console = _console()
    console.print(table)
    return console.export_text()


def render_story_text(story: Story) -> str:
    body = (
        f"Title: {story.title}\n"
        f"Author: {story.author}\n"
        f"Score: {story.score}\n"
        f"Age: {story.age}\n"
        f"Comments: {story.comment_count}\n"
        f"URL: {story.url}"
    )
    panel = Panel(body, title="Story")
    console = _console()
    console.print(panel)
    return console.export_text()


def render_comments_text(story_id: str, comments: Iterable[Comment]) -> str:
    lines = [f"Comments for story {story_id}"]
    for comment in comments:
        lines.append(f"- {comment.author} · {comment.age}")
        content = _comment_text(comment)
        if content:
            for line in content.splitlines():
                lines.append(f"  {line}")
        else:
            lines.append(f"  {_empty_marker(comment)}")
    return "\n".join(lines)


def render_link_text(story: Story) -> str:
    return story.url


def _comment_text(comment: Comment) -> str:
    content = comment.content or ""
    if not content.strip():
        return ""
    try:
        converter = html2text.HTML2Text()
        converter.body_width = 0
        converter.ignore_links = False
        return converter.handle(content).strip()
    except Exception:
        return _strip_html(content).strip()


def _strip_html(content: str) -> str:
    text = re.sub(r"<[^>]+>", "", content)
    return html.unescape(text)


def _empty_marker(comment: Comment) -> str:
    if comment.author.lower() in {"unknown", "deleted"}:
        return "[deleted]"
    return "[empty]"
