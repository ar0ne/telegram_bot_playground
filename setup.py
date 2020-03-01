import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "telegram_bot_playgroud",
    version = "0.0.1",
    author = "ar0ne",
    description = ("An example of usage Telegram Bot API."),
    license = "None",
    keywords = "telegram bot sqlalchemy",
    url = "https://github.com/ar0ne/telegram_bot_playground",
    packages=['app'],
    long_description=read('readme.md'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Programming Language :: Python',
    ],
)