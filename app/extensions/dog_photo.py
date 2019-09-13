import re
import requests

BASE_URL = 'https://random.dog/woof.json'


def get_url() -> str:
    response = requests.get(BASE_URL)
    return response.json()['url']


def get_photo_url() -> str:
    allowed_extensions = ('jpg', 'png', 'jped')
    extension = ''
    while extension not in allowed_extensions:
        url = get_url()
        extension = re.search("([^.]*)$", url).group(1).lower()
    return url
