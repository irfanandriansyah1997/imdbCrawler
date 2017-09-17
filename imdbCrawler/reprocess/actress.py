from imdbCrawler.library.mongo_pipeline import MongoPipeline
from imdbCrawler.settings import MONGODB_DB, MONGODB_HOST, MONGODB_PORT

class ActessReprocess:
    def __init__(self):
        self.db = MongoPipeline(
            MONGODB_HOST,
            MONGODB_PORT,
            MONGODB_DB
        )

    def reprocess(self):
        collection = "reprocess_item_actress"

        response = self.db.get(collection, where={"status": "checked"})
        print response.get("count")
        for item in response.get("data"):
            print item.get('id')
            for child in item.get("data"):
                print child
                status = self.db.get("actress", where={"actress_id": child})
                print status.get("count")
                if status.get("count") == 0:
                    self.db.reprocess_item("actress", child)
                    print 'insert'
                else:
                    print 'avaiable'

            self.db.updateOne(collection, {"status": "save"}, {'key': "id", 'value': str(item.get("id"))})

if __name__ == '__main__':
    a = ActessReprocess()
    a.reprocess()



