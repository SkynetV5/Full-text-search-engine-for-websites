import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from types import SimpleNamespace

import app.crawler as crawler_module
from app.crawler import SimpleCrawler


def test_crawl_url_extracts_page_text(monkeypatch):
    url = "https://example.com/"
    monkeypatch.setattr(SimpleCrawler, "can_fetch", lambda self, user_agent: True)
    monkeypatch.setattr(crawler_module.time, "sleep", lambda delay: None)
    monkeypatch.setattr(
        crawler_module.requests,
        "get",
        lambda **kwargs: SimpleNamespace(
            status_code=200,
            text="<html><body><p>Hello </p><p>world</p></body></html>",
        ),
    )
    crawler = SimpleCrawler(url=url, depth=0, delay_limit=0)

    pages = crawler.crawl_url()

    assert pages == [{"path_url": url, "text": "Hello world"}]
    assert crawler.visited == {url}


def test_crawl_url_follows_links_only_within_depth(monkeypatch):
    start_url = "https://example.com/"
    child_url = "https://example.com/child"
    responses = {
        start_url: "<p>Home</p><a href='https://example.com/child'>child</a>",
        child_url: "<p>Child</p><a href='https://example.com/too-deep'>next</a>",
    }
    requested_urls = []

    def fake_get(url, headers):
        requested_urls.append(url)
        return SimpleNamespace(status_code=200, text=responses[url])

    monkeypatch.setattr(SimpleCrawler, "can_fetch", lambda self, user_agent: True)
    monkeypatch.setattr(crawler_module.time, "sleep", lambda delay: None)
    monkeypatch.setattr(crawler_module.requests, "get", fake_get)
    crawler = SimpleCrawler(url=start_url, depth=1, delay_limit=0)

    pages = crawler.crawl_url()

    assert pages == [
        {"path_url": start_url, "text": "Homechild"},
        {"path_url": child_url, "text": "Childnext"},
    ]
    assert requested_urls == [start_url, child_url]


def test_crawl_url_respects_robots_txt(monkeypatch):
    start_url = "https://example.com/private"
    requested_urls = []

    def fake_get(url, headers):
        requested_urls.append(url)
        return SimpleNamespace(
            status_code=200,
            text="User-agent: *\nDisallow: /",
        )

    monkeypatch.setattr(crawler_module.requests, "get", fake_get)
    crawler = SimpleCrawler(url=start_url, delay_limit=0)

    pages = crawler.crawl_url()

    assert pages == []
    assert requested_urls == ["https://example.com/robots.txt"]
