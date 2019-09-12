import logging
import os

import requests
from requests import HTTPError
from PIL import Image
from io import BytesIO

BASE_URL = 'http://api.screenshotlayer.com/api/capture'


def take_screenshot(url: str = '', viewport: str = '1440x900'):
    assert url, "Requested url can't be empty!"

    access_key = os.getenv("SCREENSHOT_API_KEY")
    assert access_key, "Screenshot API Key must be not empty!"

    try:
        response = requests.get(
            BASE_URL,
            params={
                'access_key': access_key,
                'url': url,
                'viewport': viewport,
            },
            stream=True,
        )
        img = Image.open(response.raw)
        bio = BytesIO()
        bio.name = 'screenshot.png'
        img.save(bio, 'PNG')
        bio.seek(0)
        return bio

    except HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logging.error(f'Other error occurred: {err}')
