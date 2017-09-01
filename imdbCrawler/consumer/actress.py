class ActressConsumer:
    actress_id = None
    actress_link = None
    actress_name = None
    actress_photo = {}
    actress_category = []
    actress_filmography = []
    actress_height = None
    actress_birth = {}
    actress_personal_detail = {}
    actress_bio = None
    actress_media = []

    def __init__(self, data=dict()):
        if data:
            self.set_dict(data)
        else:
            self.reset_dict()

    def get_dict(self, prefix='actress_'):
        response = dict()
        response.update({'{}id'.format(prefix): self.actress_id})
        response.update({'{}link'.format(prefix): self.actress_link})
        response.update({'{}name'.format(prefix): self.actress_name})
        response.update({'{}photo'.format(prefix): self.actress_photo})
        response.update({'{}category'.format(prefix): self.actress_category})
        response.update({'{}filmography'.format(prefix): self.actress_filmography})
        response.update({'{}height'.format(prefix): self.actress_height})
        response.update({'{}birth'.format(prefix): self.actress_birth})
        response.update({'{}personal_detail'.format(prefix): self.actress_personal_detail})
        response.update({'{}bio'.format(prefix): self.actress_bio})
        response.update({'{}media'.format(prefix): self.actress_media})

        return response

    def set_dict(self, data):
        self.actress_id = str(data.get('actress_id').encode('utf-8')) if data.get('actress_id') is not None else None
        self.actress_link = str(data.get('actress_link').encode('utf-8')) if data.get('actress_link') is not None else None
        self.actress_name = str(data.get('actress_name').encode('utf-8')) if data.get('actress_name') is not None else None
        self.actress_photo = data.get('actress_photo') if data.get('actress_photo') is not None else {}
        self.actress_category = data.get('actress_category') if data.get('actress_category') is not None else []
        self.actress_filmography = data.get('actress_filmography') if data.get('actress_filmography') is not None else []
        self.actress_height = str(data.get('actress_height').encode('utf-8')) if data.get('actress_height') is not None else None
        self.actress_birth = data.get('actress_birth') if data.get('actress_birth') is not None else {}
        self.actress_personal_detail = data.get('actress_personal_detail') if data.get('actress_personal_detail') is not None else {}
        self.actress_bio = str(data.get('actress_bio').encode('utf-8')) if data.get('actress_bio') is not None else None
        self.actress_media = data.get('actress_media') if data.get('actress_media') is not None else []

    def reset_dict(self):
        self.actress_id = None
        self.actress_link = None
        self.actress_name = None
        self.actress_photo = {}
        self.actress_category = []
        self.actress_filmography = []
        self.actress_height = None
        self.actress_birth = {}
        self.actress_personal_detail = {}
        self.actress_bio = None
        self.actress_media = []



if __name__ == '__main__':
    a = ActressConsumer()
    print a.get_dict()
