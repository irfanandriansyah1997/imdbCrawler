import functools
from scrapy.exceptions import DropItem

def check_pipeline(f):
    @functools.wraps(f)
    def wrapper(self, item, spider):
        msg = '%%s %s pipeline step' % (self.__class__.__name__,)

        if self.__class__ in spider.pipeline:
            # log(msg % 'executing')
            return f(self, item, spider)
        else:
            # log(msg % 'skipping')
            return item

    return wrapper

class RequiredFieldsPipeline(object):
    """A pipeline to ensure the item have the required fields."""

    @check_pipeline
    def process_item(self, item, spider):
        print '******************************************************'
        for field in spider.required_fields:
            if not item.get(field):
                raise DropItem("Field '%s' missing: %r" % (field, item))
        return item

