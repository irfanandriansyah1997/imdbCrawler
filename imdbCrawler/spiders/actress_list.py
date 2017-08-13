import scrapy

class ActressListSpider(scrapy.Spider):
    name = "actress-list"
    allowed_domains = []
    base_url = None
    start_urls = []
    collection = None

    def __init__(self, data):
        scrapy.Spider.__init__(self)
        self.base_url = data.get('base_url')
        self.collection = data.get('collection').get('actress')
        self.allowed_domains = [x for x in data.get('allowed_domains')]
        self.start_urls.append(data.get('start_url').get('actress-list')[0])

    @classmethod
    def from_crawler(cls, crawler):
        data = dict()
        data.update({'base_url' : crawler.settings.get('BASE_URL')})
        data.update({'start_url': crawler.settings.get('START_URL')})
        data.update({'collection': crawler.settings.get('COLLECTION')})
        data.update({'allowed_domains': crawler.settings.get('ALLOWED_DOMAIN')})
        return cls(data)

    def parse(self, response):
        print response