import re
import requests

BASE_URL = 'http://aws.random.cat/meow'


def get_url() -> str:
    response = requests.get(BASE_URL)
    return response.json()['file']


def get_photo_url() -> str:
    allowed_extensions = ('jpg', 'png', 'jped')
    extension = ''
    while extension not in allowed_extensions:
        url = get_url()
        extension = re.search("([^.]*)$", url).group(1).lower()
    return url
