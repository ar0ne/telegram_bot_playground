#!/usr/bin/env python
import os

import logging
import random
import json

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from dotenv import load_dotenv

from text2speech import generate_audio

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

USERS = {}
SAY_CMD = 'say'
BIBA_CMD = 'biba'
HELP_CMD = 'help'
STATISTICS_CMD = 'stat'


# TODO: save somewhere statistic
def _calculate_uses(update):
    username = update.message.chat.username
    if username in USERS:
        USERS[username] += 1
    else:
        USERS[username] = 1


def unknown_cmd(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Твоя моя не пониматъ.")


def say_cmd(update, context):
    ending = ', кожаный ублюдок!'
    draft_message = ' '.join(context.args)
    if 0 < len(draft_message.strip()) < 250:
        _calculate_uses(update)
        message = f"{draft_message}{ending}"
        audio = generate_audio(text=message)
        context.bot.send_voice(chat_id=update.message.chat_id, voice=open(audio.name, 'rb'))
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=f'Попроси лучше{ending}')


def bibametr_cmd(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=f"Твоя биба {random.randrange(3, 26)} сантиметров!")


def help_cmd(update, context):
    commands = [
        SAY_CMD,
        BIBA_CMD,
        HELP_CMD,
        STATISTICS_CMD,
    ]
    context.bot.send_message(chat_id=update.message.chat_id, text=f"Умею и могу - {', '.join(commands)}")


def statistics_cmd(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=f"Эти ублюдки мне должны \n - {json.dumps(USERS, indent=4, sort_keys=True)}")


def main():
    load_dotenv()
    token = os.getenv("TOKEN")

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    bibametr_handler = CommandHandler(BIBA_CMD, bibametr_cmd)
    say_handler = CommandHandler(SAY_CMD, say_cmd)
    help_handler = CommandHandler(HELP_CMD, help_cmd)
    statistics_handler = CommandHandler(STATISTICS_CMD, statistics_cmd)
    unknown_handler = MessageHandler(Filters.command, unknown_cmd)

    dispatcher.add_handler(bibametr_handler)
    dispatcher.add_handler(say_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(statistics_handler)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()


if __name__ == '__main__':
    main()
