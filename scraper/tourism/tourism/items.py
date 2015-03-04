import scrapy


class TourismItem(scrapy.Item):
    place = scrapy.Field()
    content = scrapy.Field()
    details = scrapy.Field()