from __future__ import annotations

import os
import sys
import html
import re
from contextlib import contextmanager
from typing import Any, Iterable, Iterator, TextIO

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import html2text

from .models import Comment, Story


@contextmanager
def _null_console() -> Iterator[Console]:
    """Yield a Console that records output without writing to stdout.

    Uses /dev/null as the file so Rich never touches the real stdout, while
    record=True lets us retrieve the rendered text via export_text().
    """
    with open(os.devnull, "w") as null:
        console = Console(
            file=null, record=True, force_terminal=False, color_system=None, no_color=True
        )
        yield console


def _render_to_string(renderable: Any) -> str:
    """Render a Rich renderable to a plain-text string without writing to stdout."""
    with _null_console() as console:
        console.print(renderable)
        return console.export_text()


def print_json(payload: Any, stream: TextIO | None = None) -> None:
    _stream = stream if stream is not None else sys.stdout
    with _null_console() as console:
        console.print_json(data=payload)
        _stream.write(console.export_text())


def print_text(text: str, stream: TextIO | None = None) -> None:
    _stream = stream if stream is not None else sys.stdout
    _stream.write(text)


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

    return _render_to_string(table)


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
    return _render_to_string(panel)


def render_comments_text(story_id: str, comments: Iterable[Comment]) -> str:
    lines = [f"Comments for story {story_id}"]
    for comment in comments:
        indent = "  " * comment.depth
        lines.append(f"{indent}- {comment.author} · {comment.age}")
        content = _comment_text(comment)
        if content:
            for line in content.splitlines():
                lines.append(f"{indent}  {line}")
        else:
            lines.append(f"{indent}  {_empty_marker(comment)}")
    return "\n".join(lines)


def render_link_text(story: Story) -> str:
    return story.url


def render_help_text() -> str:
    """Render a formatted help overview for all CLI commands."""
    sections: list[str] = []

    # header
    with _null_console() as con:
        con.print("[bold]hn[/bold] — Hacker News CLI Reader", highlight=False)
        con.print("Usage: hn <command> [options]\n", markup=False)
        sections.append(con.export_text())

    # commands table
    cmd_table = Table(show_header=True, header_style="bold", box=None, pad_edge=False)
    cmd_table.add_column("Command", min_width=10)
    cmd_table.add_column("Description")
    for cmd, desc in [
        ("list", "List stories from a feed (default format: text)"),
        ("story", "Show details for a story"),
        ("comments", "Show comments for a story"),
        ("link", "Show the URL of a story"),
        ("help", "Show this help message"),
        ("interactive", "Start interactive mode with > prompt"),
        ("login", "Login to Hacker News"),
        ("logout", "Logout from Hacker News"),
        ("whoami", "Show current logged-in user"),
    ]:
        cmd_table.add_row(cmd, desc)
    sections.append(_render_to_string(cmd_table))

    # per-command argument tables
    command_args: list[tuple[str, list[tuple[str, str, str]]]] = [
        (
            "list",
            [
                ("--feed", "{top,new,best,ask,show,jobs}", "Feed to read (default: top)"),
                ("--limit", "INT", "Number of stories to fetch (default: 30)"),
                ("--page", "INT", "Page number (default: 1)"),
                ("--format", "{json,text}", "Output format (default: text)"),
            ],
        ),
        (
            "story / comments / link",
            [
                ("--id", "ID", "Story ID (required)"),
                ("--format", "{json,text}", "Output format (default: json)"),
            ],
        ),
        (
            "comments",
            [
                ("--depth", "INT", "Max thread depth to fetch (default: unlimited)"),
                ("--max-comments", "INT", "Max comments to fetch (default: unlimited)"),
            ],
        ),
        (
            "all commands",
            [
                ("--timeout", "FLOAT", "Request timeout in seconds (default: 10.0)"),
                ("--retries", "INT", "Max retry attempts (default: 2)"),
                ("--backoff", "FLOAT", "Retry backoff factor in seconds (default: 0.5)"),
            ],
        ),
        (
            "login",
            [
                ("--username", "TEXT", "HN username (if omitted, prompt interactively)"),
                ("--password", "TEXT", "HN password (if omitted, prompt securely)"),
                ("--timeout", "FLOAT", "Request timeout in seconds (default: 10.0)"),
                ("--retries", "INT", "Max retry attempts (default: 2)"),
                ("--backoff", "FLOAT", "Retry backoff factor in seconds (default: 0.5)"),
            ],
        ),
    ]

    for title, args in command_args:
        arg_table = Table(show_header=True, header_style="bold", box=None, pad_edge=False)
        arg_table.add_column("Option", min_width=12)
        arg_table.add_column("Value", min_width=16)
        arg_table.add_column("Description")
        for flag, meta, description in args:
            arg_table.add_row(flag, meta, description)
        sections.append(_render_to_string(Panel(arg_table, title=title, expand=False)))

    sections.append("Tip: run 'hn <command> --help' for the full argument list.\n")
    return "\n".join(sections)


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
