

import random
import logging
from scrapy.exceptions import IgnoreRequest

logger = logging.getLogger(__name__)



USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]


class RotateUserAgentMiddleware:
    """Assigns a random User-Agent header to every outgoing request."""

    def process_request(self, request, spider):
        ua = random.choice(USER_AGENTS)
        request.headers["User-Agent"] = ua


class CaptchaDetectionMiddleware:
    """
    Detects Amazon block / CAPTCHA pages so they don't get parsed as
    normal product pages (which would silently produce empty/garbage data).
    """

    BLOCK_INDICATORS = [
        "Type the characters you see in this image",
        "Enter the characters you see below",
        "/errors/validateCaptcha",
        "To discuss automated access to Amazon data",
        "Sorry, we just need to make sure you're not a robot",
        "api-services-support@amazon.com",
    ]

    def process_response(self, request, response, spider):
        body_snippet = response.text[:5000] if response.text else ""

        if response.status in (503, 429):
            logger.warning(
                "Possible rate-limit/block (HTTP %s) on %s",
                response.status,
                request.url,
            )
            raise IgnoreRequest(f"Blocked with status {response.status}")

        for indicator in self.BLOCK_INDICATORS:
            if indicator.lower() in body_snippet.lower():
                logger.warning(
                    "CAPTCHA / block page detected at %s. "
                    "Consider: slowing down DOWNLOAD_DELAY, rotating proxies, "
                    "or switching to the Selenium fallback script.",
                    request.url,
                )
                raise IgnoreRequest("CAPTCHA page detected")

        return response


class ProxyMiddleware:
    """
    Optional proxy rotation middleware. Disabled by default in settings.py.

    To use:
      1. Fill PROXIES below with proxies from your provider, e.g.:
         "http://user:pass@proxyhost1:port"
      2. Enable this middleware in settings.py DOWNLOADER_MIDDLEWARES.

    For Amazon specifically, free/public proxies are almost always
    already blacklisted -- use a paid residential/rotating proxy service
    for anything beyond small portfolio-scale scraping.
    """

    PROXIES = [
        # "http://user:pass@proxy1.example.com:8000",
        # "http://user:pass@proxy2.example.com:8000",
    ]

    def process_request(self, request, spider):
        if self.PROXIES:
            request.meta["proxy"] = random.choice(self.PROXIES)
