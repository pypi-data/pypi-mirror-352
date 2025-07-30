scrapy-scrapingfish
===================

A Scrapy downloader middleware for ScrapingFish.


## Installation
```bash
pip install scrapy-scrapingfish
```

## Configuration
Add the following to your Scrapy settings `settings.py` file:
```python
DOWNLOADER_MIDDLEWARES = {
    # Adjust priorty as needed
    'scrapy_scrapingfish.middleware.ScrapingFishProxyMiddleware': 760,
}

Set your ScrapingFish API key:
```python
SCRAPINGFISH_API_KEY = "YOUR_SCRAPINGFISH_API_KEY"
```

## Supported parameters
- `SCRAPINGFISH_API_KEY: str` - Your ScrapingFish API key.
- `SCRAPINGFISH_REQUEST_PARAMS: dict` Additional settings for ScrapingFish requests based on official documentation.
- `SCRAPINGFISH_TIMEOUT: int` - Timeout for requests in seconds. Default is `90`.
