#!/usr/bin/env python
import os

import logging
import random

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from dotenv import load_dotenv

from text2speech import generate_audio

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def unknown(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


def say_cmd(update, context):
    ending = ', кожаный ублюдок!'
    draft_message = ' '.join(context.args)
    if 0 < len(draft_message.strip()) < 250:
        message = f"{draft_message}{ending}"
        audio = generate_audio(text=message)
        context.bot.send_voice(chat_id=update.message.chat_id, voice=open(audio.name, 'rb'))
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=f'Попроси лучше{ending}')


def bibametr_cmd(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=f"Твоя биба {random.randrange(3, 26)} сантиметров!")


def help_cmd(update, context):
    commands = [
        'say',
        'biba',
    ]
    context.bot.send_message(chat_id=update.message.chat_id, text=f"Команды: {','.join(commands)}")


def main():
    load_dotenv()
    token = os.getenv("TOKEN")

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    bibametr_handler = CommandHandler('biba', bibametr_cmd)
    say_handler = CommandHandler('say', say_cmd)
    help_handler = CommandHandler('help', help_cmd)
    unknown_handler = MessageHandler(Filters.command, unknown)

    dispatcher.add_handler(bibametr_handler)
    dispatcher.add_handler(say_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()


if __name__ == '__main__':
    main()
