# How to use

* `$ pipenv install`
* Create copy of `.env.example` file with `.env` name and fill up required properties.
* ...TBA

# AWS boto3

Boto3 will check these environment variables for credentials:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

# Supported commands:

## /say <text>

This command generate voice audio from `text` which you send to bot. Under the hood, bot uses AWS Polly service which does text to speech transformation.

## /biba

Using last decisions in machine learning and neural networks area, bot tries to predict your `biba` size.

## /help

See help message.

## /shot <url>

Bot responds with a screenshot of requested url.

