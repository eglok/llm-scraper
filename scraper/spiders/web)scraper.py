import scrapy
from scrapy_playwright.page import PageCoroutine
from urllib.parse import urljoin

class WebScraperSpider(scrapy.Spider):
    name = "web_scraper"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/articles"]

    # Respect robots.txt: This is enabled by default in Scrapy if you set ROBOTSTXT_OBEY=True.
    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
    }

    async def parse(self, response):
        # Only scrape if allowed by the site's robots.txt
        for article in response.css("div.article"):
            relative_url = article.css("a::attr(href)").get()
            absolute_url = urljoin(response.url, relative_url)
            yield scrapy.Request(absolute_url, callback=self.parse_article)

    async def parse_article(self, response):
        yield {
            "url": response.url,
            "title": response.css("h1::text").get(),
            "content": " ".join(response.css("div.content p::text").getall()),
        }
