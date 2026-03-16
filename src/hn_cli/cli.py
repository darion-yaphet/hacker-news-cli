from __future__ import annotations

import argparse
import sys
from typing import Any

from .client import HNClient, HNClientError
from .output import comments_output, link_output, story_detail_output, story_list_output
from .render import print_error, print_json


class CLIError(Exception):
    pass


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # pragma: no cover - exercised via run
        raise CLIError(message)


def build_parser() -> JsonArgumentParser:
    parser = JsonArgumentParser(prog="hn", description="Hacker News CLI Reader")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List stories from a feed")
    list_parser.add_argument("--feed", default="top", choices=HNClient.FEED_MAP.keys())
    list_parser.add_argument("--limit", type=int, default=30)
    list_parser.add_argument("--page", type=int, default=1)

    story_parser = subparsers.add_parser("story", help="Show story details")
    story_parser.add_argument("--id", required=True)

    comments_parser = subparsers.add_parser("comments", help="Show story comments")
    comments_parser.add_argument("--id", required=True)

    link_parser = subparsers.add_parser("link", help="Show story link")
    link_parser.add_argument("--id", required=True)

    return parser


def handle_list(args: argparse.Namespace, client: HNClient) -> dict[str, Any]:
    stories = client.list_stories(args.feed, args.limit, args.page)
    return story_list_output(args.feed, args.page, stories)


def handle_story(args: argparse.Namespace, client: HNClient) -> dict[str, Any]:
    story = client.get_story(args.id)
    return story_detail_output(story)


def handle_comments(args: argparse.Namespace, client: HNClient) -> dict[str, Any]:
    comments = client.get_comments(args.id)
    return comments_output(str(args.id), comments)


def handle_link(args: argparse.Namespace, client: HNClient) -> dict[str, Any]:
    story = client.get_story(args.id)
    return link_output(story)


def run(argv: list[str], client: HNClient | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except CLIError as exc:
        print_error(str(exc), code=2)
        return 2

    client = client or HNClient()

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
        print_json(payload)
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
