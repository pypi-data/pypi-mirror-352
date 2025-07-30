import pytest

from unittest.mock import MagicMock, patch

from scrapy.http import Request
from scrapy.exceptions import NotConfigured

from scrapy_scrapingfish import ScrapingFishProxyMiddleware


@pytest.fixture
def crawler_mock():
    crawler = MagicMock()
    crawler.settings.get.side_effect = lambda k, d=None: {
        "SCRAPINGFISH_API_KEY": "test_api_key",
        "SCRAPINGFISH_TIMEOUT": 30,
        "SCRAPINGFISH_REQUEST_PARAMS": {"foo": "bar"},
    }.get(k, d)
    return crawler


def test_from_crawler_success(crawler_mock):
    middleware = ScrapingFishProxyMiddleware.from_crawler(crawler_mock)
    assert middleware.api_key == "test_api_key"
    assert middleware.timeout == 30
    assert middleware.settings == crawler_mock.settings.get(
        "SCRAPINGFISH_REQUEST_PARAMS", {}
    )


def test_from_crawler_missing_key():
    crawler = MagicMock()
    crawler.settings.get.side_effect = (
        lambda k, d=None: None if k == "SCRAPINGFISH_API_KEY" else d
    )

    with pytest.raises(NotConfigured):
        ScrapingFishProxyMiddleware.from_crawler(crawler)


@patch("scrapy_scrapingfish.middleware.requests.get")
def test_process_request_success(mock_get):
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.content = b"<html><body>Success</body></html>"
    mock_get.return_value = response_mock

    spider = MagicMock()
    spider.settings.get.return_value = "test_api_key"

    middleware = ScrapingFishProxyMiddleware(
        api_key="test_api_key", settings={"foo": "baz"}
    )
    request = Request(url="http://example.com")

    result = middleware.process_request(request, spider)

    assert result.status == 200
    assert b"Success" in result.body
    mock_get.assert_called_once_with(
        "https://scraping.narf.ai/api/v1/",
        params={"api_key": "test_api_key", "url": "http://example.com", "foo": "baz"},
        timeout=90,
    )


@patch("scrapy_scrapingfish.middleware.requests.get")
def test_process_request_401(mock_get):
    response_mock = MagicMock()
    response_mock.status_code = 401
    mock_get.return_value = response_mock

    spider = MagicMock()
    spider.logger = MagicMock()

    middleware = ScrapingFishProxyMiddleware(api_key="test_api_key", settings={})
    request = Request(url="http://example.com")

    result = middleware.process_request(request, spider)

    assert result is None
    spider.logger.error.assert_called_with("Bad API key or no more credits available")
