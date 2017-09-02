class FilmConsumer:
    film_id = None
    film_year = {}
    film_type = None
    film_title = None
    film_length = None
    film_photo = {}
    film_rating = {}
    film_genre = []
    film_description_short = None
    film_director = {}
    film_writer = {}
    film_stars = {}
    film_creator = {}
    film_date_release = None
    film_content_rating = None
    film_storyline = None


    def __init__(self, data=dict()):
        if data:
            self.set_dict(data)
        else:
            self.reset_dict()

    def get_dict(self, prefix='film_'):
        response = dict()
        response.update({'{}id'.format(prefix): self.film_id})
        response.update({'{}year'.format(prefix): self.film_year})
        response.update({'{}type'.format(prefix): self.film_type})
        response.update({'{}title'.format(prefix): self.film_title})
        response.update({'{}genre'.format(prefix): self.film_genre})
        response.update({'{}photo'.format(prefix): self.film_photo})
        response.update({'{}length'.format(prefix): self.film_length})
        response.update({'{}rating'.format(prefix): self.film_rating})
        response.update({'{}description_short'.format(prefix): self.film_description_short})
        response.update({'{}director'.format(prefix): self.film_director})
        response.update({'{}writer'.format(prefix): self.film_writer})
        response.update({'{}stars'.format(prefix): self.film_stars})
        response.update({'{}creator'.format(prefix): self.film_creator})
        response.update({'{}date_release'.format(prefix): self.film_date_release})
        response.update({'{}content_rating'.format(prefix): self.film_content_rating})
        response.update({'{}storyline'.format(prefix): self.film_storyline})

        return response

    def set_dict(self, data):
        self.film_id = str(data.get('film_id')).encode('utf-8') if data.get('film_id') is not None else None
        self.film_year = data.get('film_year') if data.get('film_year') is not None else {}
        self.film_type = str(data.get('film_type')).encode('utf-8') if data.get('film_type') is not None else None
        self.film_title = str(data.get('film_title')).encode('utf-8') if data.get('film_title') is not None else None
        self.film_length = str(data.get('film_length')).encode('utf-8') if data.get('film_length') is not None else None
        self.film_photo = data.get('film_photo') if data.get('film_photo') is not None else {}
        self.film_rating = data.get('film_rating') if data.get('film_rating') is not None else {}
        self.film_genre = data.get('film_genre') if data.get('film_genre') is not None else []
        self.film_description_short = str(data.get('film_description_short')).encode('utf-8') if data.get('film_description_short') is not None else None
        self.film_director = data.get('film_director') if data.get('film_director') is not None else {}
        self.film_writer = data.get('film_writer') if data.get('film_writer') is not None else {}
        self.film_stars = data.get('film_stars') if data.get('film_stars') is not None else {}
        self.film_creator = data.get('film_creator') if data.get('film_creator') is not None else {}
        self.film_date_release = data.get('film_date_release') if data.get('film_date_release') is not None else None
        self.film_content_rating = str(data.get('film_content_rating')).encode('utf-8') if data.get('film_content_rating') is not None else None
        self.film_storyline = str(data.get('film_storyline')).encode('utf-8') if data.get('film_storyline') is not None else None

    def reset_dict(self):
        self.film_id = None
        self.film_year = {}
        self.film_type= None
        self.film_title = None
        self.film_length = None
        self.film_photo = {}
        self.film_rating = {}
        self.film_genre = []
        self.film_description_short = None
        self.film_director = {}
        self.film_writer = {}
        self.film_stars = {}
        self.film_creator = {}
        self.film_date_release = None
        self.film_content_rating = None
        self.film_storyline = None

if __name__ == '__main__':
    a = FilmConsumer()
    print a.get_dict()
