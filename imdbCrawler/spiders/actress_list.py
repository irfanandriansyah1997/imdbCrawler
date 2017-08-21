import re
import scrapy

from imdbCrawler.items import ActressList
from imdbCrawler.library.mongo_pipeline import MongoPipeline
from imdbCrawler.library.general_function import convert_photo
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
    required_fields = ["actress_id", "actress_link", "actress_name", "actress_photo"]
    mongo_requirement = {
        "primary": "actress_id",
        "collection": "actress",
        "source": "list"
    }

    def __init__(self, data):
        scrapy.Spider.__init__(self)
        self.per_page = 50
        self.base_url = data.get("base_url")
        self.collection = data.get("collection").get("actress")
        self.allowed_domains = [x for x in data.get("allowed_domains")]
        
        self.start_urls = self.populate_start_urls(data.get("start_url").get("actress-list")[0], 4)

    def populate_start_urls(self, url, range_loop):
        return [url.replace("start=0", "start={}".format(index * self.per_page)) for index in range(0, range_loop)]

    @classmethod
    def from_crawler(cls, crawler):
        data = dict()
        data.update({"base_url": crawler.settings.get("BASE_URL")})
        data.update({"start_url": crawler.settings.get("START_URL")})
        data.update({"collection": crawler.settings.get("COLLECTION")})
        data.update({"allowed_domains": crawler.settings.get("ALLOWED_DOMAIN")})
        return cls(data)

    def parse(self, response):
        products = response.css("#main > table.results > tr.detailed")
        for item in products:
            name = item.css("td.name > a::text").extract_first().strip()
            # photo
            photo = convert_photo(item.css("td.image > a > img::attr(src)").extract_first().strip())

            button = item.css("td.name > a::attr(href)").extract_first().strip()

            item = ActressList()
            item.update({"actress_id": re.sub(r"name.+?", "", button).strip("/")})
            item.update({"actress_link": response.urljoin(button)})
            item.update({"actress_name": name})
            item.update({"actress_photo": photo})

            yield item