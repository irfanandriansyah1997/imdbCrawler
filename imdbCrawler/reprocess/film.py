from imdbCrawler.library.mongo_pipeline import MongoPipeline
from imdbCrawler.settings import MONGODB_DB, MONGODB_HOST, MONGODB_PORT

class FilmReprocess:
    def __init__(self):
        self.db = MongoPipeline(
            MONGODB_HOST,
            MONGODB_PORT,
            MONGODB_DB
        )

    def reprocess(self):
        collection = "reprocess_item_film"

        response = self.db.get(collection, where={"status": "checked"})

        for item in response.get("data"):
            for child in item.get("data"):
                status = self.db.get("film", where={"film_id": child})
                if status.get("count") == 0:
                    self.db.reprocess_item("film", child)

            self.db.updateOne(collection, {"status": "save"}, {'key': "id", 'value': str(item.get("id"))})

if __name__ == '__main__':
    a = FilmReprocess()
    a.reprocess()



