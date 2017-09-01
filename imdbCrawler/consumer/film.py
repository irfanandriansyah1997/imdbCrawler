class FilmConsumer:
    film_id = None
    film_year = {}
    film_title = None
    film_length = None
    film_photo = {}
    film_rating = {}
    film_genre = []
    film_description_short = None

    def __init__(self, data=dict()):
        if data:
            self.set_dict(data)
        else:
            self.reset_dict()

    def get_dict(self, prefix='film_'):
        response = dict()
        response.update({'{}id'.format(prefix): self.film_id})
        response.update({'{}year'.format(prefix): self.film_year})
        response.update({'{}title'.format(prefix): self.film_title})
        response.update({'{}genre'.format(prefix): self.film_genre})
        response.update({'{}photo'.format(prefix): self.film_photo})
        response.update({'{}length'.format(prefix): self.film_length})
        response.update({'{}rating'.format(prefix): self.film_rating})
        response.update({'{}description_short'.format(prefix): self.film_description_short})

        return response

    def set_dict(self, data):
        self.film_id = str(data.get('film_id')).encode('utf-8') if data.get('film_id') is not None else None
        self.film_year = data.get('film_year') if data.get('film_year') is not None else {}
        self.film_title = str(data.get('film_title')).encode('utf-8') if data.get('film_title') is not None else None
        self.film_length = str(data.get('film_length')).encode('utf-8') if data.get('film_length') is not None else None
        self.film_photo = data.get('film_photo') if data.get('film_photo') is not None else {}
        self.film_rating = data.get('film_rating') if data.get('film_rating') is not None else {}
        self.film_genre = data.get('film_genre') if data.get('film_genre') is not None else []
        self.film_description_short = str(data.get('film_description_short')).encode('utf-8') if data.get('film_description_short') is not None else None

    def reset_dict(self):
        self.film_id = None
        self.film_year = {}
        self.film_title = None
        self.film_length = None
        self.film_photo = {}
        self.film_rating = {}
        self.film_genre = []
        self.film_description_short = None

if __name__ == '__main__':
    a = FilmConsumer()
    print a.get_dict()
