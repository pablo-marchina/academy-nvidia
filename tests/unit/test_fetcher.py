"""Tests for src.scraping.fetcher."""

from datetime import datetime
from unittest.mock import Mock, patch

from src.scraping.fetcher import FetchResult, fetch_page


def _mock_response(status: int = 200, text: str = "") -> Mock:
    """Build a mock ``requests.Response``."""
    reasons = {200: "OK", 404: "Not Found", 500: "Internal Server Error"}
    mock = Mock()
    mock.status_code = status
    mock.text = text
    mock.reason = reasons.get(status, "Unknown")
    return mock


@patch("src.scraping.fetcher.requests.get")
def test_fetch_success_200(mock_get: Mock) -> None:
    mock_get.return_value = _mock_response(200, "<html><body>Hello</body></html>")
    result = fetch_page("https://example.com")

    assert result.status == 200
    assert result.raw_html == "<html><body>Hello</body></html>"
    assert result.error is None
    assert isinstance(result.fetched_at, datetime)


@patch("src.scraping.fetcher.requests.get")
def test_fetch_not_found_404(mock_get: Mock) -> None:
    mock_get.return_value = _mock_response(404)
    result = fetch_page("https://example.com/not-found")

    assert result.status == 404
    assert result.raw_html == ""
    assert result.error is not None
    assert "404" in result.error


@patch("src.scraping.fetcher.requests.get")
def test_fetch_server_error_500(mock_get: Mock) -> None:
    mock_get.return_value = _mock_response(500)
    result = fetch_page("https://example.com/error")

    assert result.status == 500
    assert result.raw_html == ""
    assert result.error is not None
    assert "500" in result.error


@patch("src.scraping.fetcher.requests.get")
def test_fetch_timeout(mock_get: Mock) -> None:
    from requests.exceptions import Timeout

    mock_get.side_effect = Timeout("Connection timed out")
    result = fetch_page("https://example.com", timeout=5)

    assert result.status is None
    assert result.raw_html == ""
    assert result.error is not None
    assert "timeout" in result.error.lower()


@patch("src.scraping.fetcher.requests.get")
def test_fetch_connection_error(mock_get: Mock) -> None:
    from requests.exceptions import ConnectionError

    mock_get.side_effect = ConnectionError("DNS resolution failed")
    result = fetch_page("https://example.com")

    assert result.status is None
    assert result.raw_html == ""
    assert result.error is not None
    assert "connection" in result.error.lower()


def test_fetch_invalid_url() -> None:
    result = fetch_page("not-a-url")

    assert result.status is None
    assert result.raw_html == ""
    assert result.error is not None
    assert "invalid" in result.error.lower()


def test_fetch_result_dataclass_fields() -> None:
    dt = datetime.now()
    result = FetchResult(
        url="https://example.com",
        status=200,
        raw_html="<html/>",
        fetched_at=dt,
        error=None,
    )

    assert result.url == "https://example.com"
    assert result.status == 200
    assert result.raw_html == "<html/>"
    assert result.fetched_at == dt
    assert result.error is None
