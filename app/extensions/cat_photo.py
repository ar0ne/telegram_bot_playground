import os
import re
import requests

from typing import Optional

BASE_URL = os.getenv("CAT_PHOTO_URL", 'http://aws.random.cat/meow')
WHITELISTED_FILE_EXTENSIONS = ('jpg', 'png', 'jpeg')


def get_url() -> str:
    response = requests.get(BASE_URL)
    return response.json()['file']


def get_photo_url() -> Optional[str]:
    extension = None
    url = None
    while extension not in WHITELISTED_FILE_EXTENSIONS:
        url = get_url()
        match = re.search(r"([^.]*)$", url)
        if match:
            extension = match.group(1).lower()
    return url
