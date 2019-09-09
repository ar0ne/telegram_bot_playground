#!/usr/bin/env python

import sys
import boto3

from contextlib import closing

import logging
from typing import BinaryIO

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def generate_audio(language: str = 'ru-RU', voice: str = 'Maxim', text: str = None) -> BinaryIO:
    client = boto3.client('polly')

    response = client.synthesize_speech(
        Engine='standard',
        LanguageCode=language,
        OutputFormat='mp3',
        Text=text,
        TextType='text',
        VoiceId=voice,
    )

    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            try:
                # Open a file for writing the output as a binary stream
                with open("temp.mp3", "wb") as file:
                    file.write(stream.read())
                    return file
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                sys.exit(-1)


if __name__ == '__main__':
    # generate_audio('Что ты от меня хочешь, кожанный ублюдок!')
    pass
