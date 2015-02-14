import scrapy
import urlparse

from tourism.items import TourismItem


class TripAdvisor(scrapy.Spider):
    name =  "tripadvisor"
    allowed_domains = ["tripadvisor.com.ph"]
    start_urls = [
        "http://www.tripadvisor.com.ph/Attractions-g294248-Activities-Luzon.html",
    ]

    def parse(self, response):
        item_urls = response.xpath("//div[@class='listing']//div[@class='quality easyClear']//a/@href").extract()

        for url in item_urls:
            item_url = urlparse.urljoin(response.url, url)
            yield scrapy.Request(item_url, self.parseItem)

    def parseItem(self, response):
        item = TourismItem()
        item['content'] = response.xpath("//div[@class='reviewSelector ']//div[@class='quote ']//span[@class='noQuotes']/text()").extract()
        yield item