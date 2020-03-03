#!/usr/bin/env python
import os
import logging
import boto3

from typing import BinaryIO
from contextlib import closing
from tempfile import NamedTemporaryFile


def generate_audio(language: str = 'ru-RU', voice: str = 'Maxim', text: str = None) -> BinaryIO:
    client = boto3.client('polly', region_name=os.getenv("AWS_DEFAULT_REGION"))

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
                with NamedTemporaryFile(delete=False) as file:
                    file.write(stream.read())
                    return file
            except IOError as error:
                # Could not write to file, exit gracefully
                logging.error(error)
