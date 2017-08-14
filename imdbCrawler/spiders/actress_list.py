import re
import scrapy

from imdbCrawler.items import ActressList
from imdbCrawler.library.mongo_pipeline import MongoPipeline
from imdbCrawler.library.required_fields_pipeline import RequiredFieldsPipeline

class ActressListSpider(scrapy.Spider):
    name = "actress-list"
    allowed_domains = []
    base_url = None
    start_urls = []
    collection = None
    pipeline = set([
        MongoPipeline,
        RequiredFieldsPipeline,

    ])
    required_fields = ['actress_id', 'actress_link', 'actress_name', 'actress_photo']

    def __init__(self, data):
        scrapy.Spider.__init__(self)
        self.base_url = data.get('base_url')
        self.collection = data.get('collection').get('actress')
        self.allowed_domains = [x for x in data.get('allowed_domains')]
        self.start_urls.append(data.get('start_url').get('actress-list')[0])

        print self.start_urls

    @classmethod
    def from_crawler(cls, crawler):
        data = dict()
        data.update({'base_url' : crawler.settings.get('BASE_URL')})
        data.update({'start_url': crawler.settings.get('START_URL')})
        data.update({'collection': crawler.settings.get('COLLECTION')})
        data.update({'allowed_domains': crawler.settings.get('ALLOWED_DOMAIN')})
        return cls(data)

    def parse(self, response):
        products = response.css('#main > table.results > tr.detailed')
        for item in products:
            name = item.css('td.name > a::text').extract_first().strip()
            photo = item.css('td.image > a > img::attr(src)').extract_first().strip()
            button = item.css('td.name > a::attr(href)').extract_first().strip()

            item = ActressList()
            item.update({})
            item.update({'actress_id' : re.sub(r'name.+?', '', button).strip('/')})
            item.update({'actress_link' : response.urljoin(button)})
            item.update({'actress_name' : name})
            item.update({'actress_photo' : photo})

            yield item