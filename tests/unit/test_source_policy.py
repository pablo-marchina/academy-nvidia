from src.extraction.schemas import SourceType
from src.scraping.source_policy import classify_source, is_allowed_source


def test_classify_news_source() -> None:
    assert classify_source("https://neofeed.com.br/startups/exemplo") == SourceType.NEWS


def test_block_login_source() -> None:
    assert is_allowed_source("https://example.com/login") is False


def test_allow_public_source() -> None:
    assert is_allowed_source("https://example.com/blog/post") is True
