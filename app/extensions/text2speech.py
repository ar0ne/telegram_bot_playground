#!/usr/bin/env python
import os
import logging
import boto3

from typing import Optional, IO
from contextlib import closing
from tempfile import NamedTemporaryFile


def generate_audio(
        language: Optional[str] = None,
        voice: Optional[str] = None,
        text: str = ''
) -> Optional[IO[bytes]]:
    """ Transform text into speech and provides audio file (mp3) as binary array """
    language = language or os.getenv("T2S_LANGUAGE", 'ru-RU')
    voice = voice or os.getenv("T2S_VOICE", 'Maxim')

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
    return None
