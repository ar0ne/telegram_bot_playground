# How to use

* `$ pipenv install`
* Create copy of `.env.example` file with `.env` name and fill up required properties.
* ...TBA

# AWS boto3

Boto3 will check these environment variables for credentials:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

# Supported commands:

## /say `<text>`

This command generate voice audio from `text` which you send to bot. Under the hood, bot uses AWS Polly service which does text to speech transformation.

## /biba

Using last decisions in machine learning and neural networks area, bot tries to predict your `biba` size.

## /shot `<url>`

Bot responds with a screenshot of requested url.

## /ping

Health check command.

## /help

See help message.

## /`statistics_cmd`

Show statistics of command usage by users. Keep in mind, bot will not capture statistic for command if it is not present in database (table `commands`).
First of all, you need to add them manually.

## /`secret_exit_cmd`

You can setup secret command for emergency stop of the bot.

## /woof

Get random doggy photo

## /meow

Get random kitty photo.


*Note*: You can specify own command names via environment variables, e.g. override `/stat` and `/secret_exit_cmd`.


# Deployment

* Install ansible on your host and destination server

* Add group to `/etc/ansible/hosts`

E.g. 

```
[telegram_bot_ec2]
your_ec2_instance.amazonaws.com
```

* Run playbook:

`$ cd playbook; ansible-playbook main.yml`