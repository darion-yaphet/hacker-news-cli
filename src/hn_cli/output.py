from __future__ import annotations

from typing import Iterable

from .models import Comment, Story


def story_to_dict(story: Story) -> dict:
    return {
        "id": story.id,
        "title": story.title,
        "author": story.author,
        "score": story.score,
        "age": story.age,
        "comment_count": story.comment_count,
        "url": story.url,
    }


def comment_to_dict(comment: Comment) -> dict:
    return {
        "id": comment.id,
        "author": comment.author,
        "age": comment.age,
        "content": comment.content,
        "parent_id": comment.parent_id,
        "depth": comment.depth,
    }


def story_list_output(feed: str, page: int, stories: Iterable[Story]) -> dict:
    return {
        "feed": feed,
        "page": page,
        "items": [story_to_dict(story) for story in stories],
    }


def story_detail_output(story: Story) -> dict:
    return story_to_dict(story)


def comments_output(story_id: str, comments: Iterable[Comment]) -> dict:
    return {
        "story_id": story_id,
        "comments": [comment_to_dict(comment) for comment in comments],
    }


def link_output(story: Story) -> dict:
    return {
        "id": story.id,
        "url": story.url,
    }
