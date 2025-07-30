import requests

from scrapy.http import HtmlResponse
from scrapy.exceptions import NotConfigured


class ScrapingFishProxyMiddleware:
    def __init__(self, api_key, timeout=90, settings=None):
        self.api_key = api_key
        self.timeout = timeout
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        api_key = crawler.settings.get("SCRAPINGFISH_API_KEY")
        if not api_key:
            raise NotConfigured("SCRAPINGFISH_API_KEY is not set in settings.py")

        return cls(
            api_key=api_key,
            timeout=crawler.settings.get("SCRAPINGFISH_TIMEOUT", 90),
            settings=crawler.settings.get("SCRAPINGFISH_REQUEST_PARAMS", {}),
        )

    def process_request(self, request, spider):
        payload = {
            "api_key": spider.settings.get("SCRAPINGFISH_API_KEY"),
            "url": request.url,
        }
        payload.update(self.settings)
        proxy_response = requests.get(
            "https://scraping.narf.ai/api/v1/", params=payload, timeout=self.timeout
        )
        if proxy_response.status_code == 401:
            spider.logger.error("Bad API key or no more credits available")
            return None

        return HtmlResponse(
            url=request.url,
            status=proxy_response.status_code,
            body=proxy_response.content,
            encoding="utf-8",
            request=request,
        )
