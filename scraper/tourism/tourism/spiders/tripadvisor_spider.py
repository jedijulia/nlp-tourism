import scrapy
import urlparse

from tourism.items import TourismItem


class TripAdvisor(scrapy.Spider):
    name =  "tripadvisor"
    allowed_domains = ["tripadvisor.com.ph"]
    start_urls = [
        "http://www.tripadvisor.com.ph/Attractions-g294248-Activities-Luzon.html",
        "http://www.tripadvisor.com.ph/Attractions-g294252-Activities-Mindanao.html",
        "http://www.tripadvisor.com.ph/Attractions-g298465-Activities-Panay_Island_Visayas.html",
        "http://www.tripadvisor.com.ph/Attractions-g294261-Activities-Cebu_Island_Visayas.html",
        "http://www.tripadvisor.com.ph/Attractions-g294255-Activities-Palawan_Island_Palawan_Province_Mimaropa.html",
        "http://www.tripadvisor.com.ph/Attractions-g298463-Activities-Negros_Island_Visayas.html",
        "http://www.tripadvisor.com.ph/Attractions-g298573-Activities-Manila_Metro_Manila_Luzon.html",
        "http://www.tripadvisor.com.ph/Attractions-g298467-Activities-Samar_Island_Visayas.html",
        "http://www.tripadvisor.com.ph/Attractions-g294260-Activities-Boracay_Aklan_Province_Panay_Island_Visayas.html",
        "http://www.tripadvisor.com.ph/Attractions-g294253-Activities-Mindoro.html",
        "http://www.tripadvisor.com.ph/Attractions-g298460-Activities-Cebu_City_Cebu_Island_Visayas.html",
        "http://www.tripadvisor.com.ph/Attractions-g298462-Activities-Leyte_Island_Visayas.html",
        "http://www.tripadvisor.com.ph/Attractions-g294259-Activities-Bohol_Island_Bohol_Province_Visayas.html",
        "http://www.tripadvisor.com.ph/Attractions-g298450-Activities-Makati_Metro_Manila_Luzon.html",
        "http://www.tripadvisor.com.ph/Attractions-g294256-Activities-El_Nido_Palawan_Island_Palawan_Province_Mimaropa.html",
        "http://www.tripadvisor.com.ph/Attractions-g298459-Activities-Davao_City_Davao_del_Sur_Province_Mindanao.html",
        "http://www.tripadvisor.com.ph/Attractions-g298574-Activities-Quezon_City_Metro_Manila_Luzon.html",
        "http://www.tripadvisor.com.ph/Attractions-g298445-Activities-Baguio_Benguet_Province_Cordillera_Region_Luzon.html",
        "http://www.tripadvisor.com.ph/Attractions-g294257-Activities-Puerto_Princesa_Palawan_Island_Palawan_Province_Mimaropa.html",
        "http://www.tripadvisor.com.ph/Attractions-g616032-Activities-Dumaguete_City_Negros_Oriental_Negros_Island_Visayas.html"

    ]

    def parse(self, response):
        # item_urls = response.xpath("//div[@class='listing']//div[@class='quality easyClear']//a/@href").extract()
        item_urls = response.xpath("//div[@class='entry']/div[@class='property_title']//a/@href").extract()

        for url in item_urls:
            item_url = urlparse.urljoin(response.url, url)
            yield scrapy.Request(item_url, self.parseItem)

    def parseItem(self, response):
        item = TourismItem()
        item['place'] = response.xpath("//h1[@id='HEADING']/text()").extract()
        item['content'] = response.xpath("//div[@class='reviewSelector ']//div[@class='quote ']//span[@class='noQuotes']/text()").extract()
        item['details'] = response.xpath("//div[@class='reviewSelector ']//div[@class='entry']/p/text()").extract()
        yield item