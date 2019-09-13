import re
import requests


def get_url() -> str:
    response = requests.get('http://aws.random.cat/meow')
    return response.json()['file']


def get_photo_url() -> str:
    allowed_extensions = ('jpg', 'png', 'jped')
    extension = ''
    while extension not in allowed_extensions:
        url = get_url()
        extension = re.search("([^.]*)$", url).group(1).lower()
    return url