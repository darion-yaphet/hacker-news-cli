import pytest

from hn_cli.client import HNClient


def test_feed_endpoint_valid():
    assert HNClient.feed_endpoint("top") == "topstories"
    assert HNClient.feed_endpoint("new") == "newstories"


def test_feed_endpoint_invalid():
    with pytest.raises(ValueError):
        HNClient.feed_endpoint("unknown")
