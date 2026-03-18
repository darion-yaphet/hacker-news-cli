from __future__ import annotations

import argparse
import shlex
import sys
from dataclasses import dataclass
from typing import Any, Callable, NoReturn

from .client import HNClient, HNClientError
from .output import comments_output, link_output, story_detail_output, story_list_output
from .render import (
    print_error,
    print_json,
    print_text,
    render_comments_text,
    render_help_text,
    render_link_text,
    render_list_text,
    render_story_text,
)


class CLIError(Exception):
    pass


@dataclass(frozen=True)
class OutputPayload:
    kind: str
    data: Any


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:  # pragma: no cover - exercised via run
        raise CLIError(message)


def build_parser() -> JsonArgumentParser:
    parser = JsonArgumentParser(prog="hn", description="Hacker News CLI Reader")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List stories from a feed")
    list_parser.add_argument("--feed", default="top", choices=HNClient.FEED_MAP.keys())
    list_parser.add_argument("--limit", type=int, default=30)
    list_parser.add_argument("--page", type=int, default=1)
    _add_client_arguments(list_parser)
    list_parser.add_argument("--format", choices=("json", "text"), default="text")

    story_parser = subparsers.add_parser("story", help="Show story details")
    story_parser.add_argument("--id", required=True)
    _add_client_arguments(story_parser)
    _add_format_argument(story_parser)

    comments_parser = subparsers.add_parser("comments", help="Show story comments")
    comments_parser.add_argument("--id", required=True)
    _add_client_arguments(comments_parser)
    _add_format_argument(comments_parser)

    link_parser = subparsers.add_parser("link", help="Show story link")
    link_parser.add_argument("--id", required=True)
    _add_client_arguments(link_parser)
    _add_format_argument(link_parser)

    subparsers.add_parser("help", help="Show help for all commands")
    subparsers.add_parser("interactive", help="Start interactive mode with > prompt")

    return parser


def _add_format_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=("json", "text"), default="json")


def _add_client_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--backoff", type=float, default=0.5)


def handle_list(args: argparse.Namespace, client: HNClient) -> OutputPayload:
    stories = client.list_stories(args.feed, args.limit, args.page)
    return OutputPayload("list", {"feed": args.feed, "page": args.page, "stories": stories})


def handle_story(args: argparse.Namespace, client: HNClient) -> OutputPayload:
    story = client.get_story(args.id)
    return OutputPayload("story", story)


def handle_comments(args: argparse.Namespace, client: HNClient) -> OutputPayload:
    comments = client.get_comments(args.id)
    return OutputPayload("comments", {"story_id": str(args.id), "comments": comments})


def handle_link(args: argparse.Namespace, client: HNClient) -> OutputPayload:
    story = client.get_story(args.id)
    return OutputPayload("link", story)


def output_payload(payload: OutputPayload, output_format: str) -> None:
    if output_format == "text":
        if payload.kind == "list":
            text = render_list_text(
                payload.data["feed"], payload.data["page"], payload.data["stories"]
            )
        elif payload.kind == "story":
            text = render_story_text(payload.data)
        elif payload.kind == "comments":
            text = render_comments_text(payload.data["story_id"], payload.data["comments"])
        elif payload.kind == "link":
            text = render_link_text(payload.data)
        else:
            raise CLIError("Unknown command")
        print_text(text)
        return

    if payload.kind == "list":
        print_json(
            story_list_output(payload.data["feed"], payload.data["page"], payload.data["stories"])
        )
    elif payload.kind == "story":
        print_json(story_detail_output(payload.data))
    elif payload.kind == "comments":
        print_json(comments_output(payload.data["story_id"], payload.data["comments"]))
    elif payload.kind == "link":
        print_json(link_output(payload.data))
    else:
        raise CLIError("Unknown command")


def run(argv: list[str], client: HNClient | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except CLIError as exc:
        print_error(str(exc), code=2)
        return 2

    if args.command == "help":
        print_text(render_help_text())
        return 0
    if args.command == "interactive":
        return run_interactive()

    client = client or HNClient(
        timeout=args.timeout,
        max_retries=args.retries,
        backoff=args.backoff,
    )

    try:
        if args.command == "list":
            payload = handle_list(args, client)
        elif args.command == "story":
            payload = handle_story(args, client)
        elif args.command == "comments":
            payload = handle_comments(args, client)
        elif args.command == "link":
            payload = handle_link(args, client)
        else:
            raise CLIError("Unknown command")
        output_payload(payload, args.format)
        return 0
    except HNClientError as exc:
        print_error(str(exc), code=1)
        return 1
    except NotImplementedError:
        print_error("Not implemented", code=1)
        return 1
    except CLIError as exc:
        print_error(str(exc), code=2)
        return 2


def main() -> None:
    sys.exit(run(sys.argv[1:]))


def run_interactive(
    *,
    input_fn: Callable[[str], str] = input,
    runner: Callable[[list[str]], int] | None = None,
) -> int:
    """Start interactive mode and execute one command per input line."""
    run_command = runner if runner is not None else run
    print_text("Interactive mode. Type 'help' for commands, 'exit' or 'quit' to leave.\n")

    while True:
        try:
            line = input_fn("> ")
        except EOFError:
            print_text("\n")
            return 0
        except KeyboardInterrupt:
            print_text("\n")
            return 0

        text = line.strip()
        if not text:
            continue
        if text.startswith("hn "):
            text = text[3:].strip()
        if text.lower() in {"exit", "quit"}:
            return 0

        try:
            argv = shlex.split(text)
        except ValueError as exc:
            print_error(str(exc), code=2)
            continue

        if not argv:
            continue
        if argv[0] == "interactive":
            print_text("Already in interactive mode.\n")
            continue

        try:
            run_command(argv)
        except KeyboardInterrupt:
            print_text("\n")
            continue
