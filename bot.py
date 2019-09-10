#!/usr/bin/env python
import os

import logging
import random
import json
import threading

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from dotenv import load_dotenv
from functools import wraps

from dao.db import DataBaseConnector, UserDao, CommandDao, StatisticsDao
from extensions.text2speech import generate_audio
from extensions.screenshoter import take_screenshot

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class TelegramBot:
    def __init__(self, token: str, db_url: str):
        self._token = token
        self._updater = Updater(token=token, use_context=True)
        self._dispatcher = self._updater.dispatcher

        self.SAY_CMD = 'say'
        self.BIBA_CMD = 'biba'
        self.HELP_CMD = 'help'
        self.STATISTICS_CMD = 'stat'
        self.EXIT_CMD = os.getenv('EXIT_COMMAND')
        self.SCREENSHOT_CMD = 'shot'

        self.db = DataBaseConnector(db_url)

        self.userDao = UserDao(self.db)
        self.cmdDao = CommandDao(self.db)
        self.statDao = StatisticsDao(self.db)

    def init_handlers(self):
        bibametr_handler = CommandHandler(self.BIBA_CMD, self.bibametr_cmd)
        say_handler = CommandHandler(self.SAY_CMD, self.say_cmd)
        help_handler = CommandHandler(self.HELP_CMD, self.help_cmd)
        statistics_handler = CommandHandler(self.STATISTICS_CMD, self.statistics_cmd)
        unknown_handler = MessageHandler(Filters.command, self.unknown_cmd)
        secret_exit_handler = CommandHandler(self.EXIT_CMD, self.secret_exit_cmd)
        screenshot_handler = CommandHandler(self.SCREENSHOT_CMD, self.screenshot_cmd)

        self._dispatcher.add_handler(bibametr_handler)
        self._dispatcher.add_handler(say_handler)
        self._dispatcher.add_handler(help_handler)
        self._dispatcher.add_handler(statistics_handler)
        self._dispatcher.add_handler(secret_exit_handler)
        self._dispatcher.add_handler(screenshot_handler)
        self._dispatcher.add_handler(unknown_handler)

    def start(self):
        self._updater.start_polling()
        self._updater.idle()

    def log_event(fn):
        @wraps(fn)
        def wrapped(self, *args, **kwargs):
            user_id = args[0].message.from_user.id
            user = self.userDao.get_by_id(user_id)

            if user:
                command_name = args[0].message.text.replace('/', '')
                command = self.cmdDao.get_by_name(command_name)
                if command:
                    self.statDao.increment(user['id'], command['id'])
            else:
                self.userDao.add(
                    id=user_id,
                    username=args[0].message.from_user.username,
                    first_name=args[0].message.from_user.first_name,
                    last_name=args[0].message.from_user.last_name
                )

            fn(self, *args, **kwargs)

        return wrapped

    def unknown_cmd(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id, text="Твоя моя не пониматъ.")

    @log_event
    def say_cmd(self, update, context):
        ending = ', кожаный ублюдок!'
        draft_message = ' '.join(context.args).strip()
        if 0 < len(draft_message) < 250:
            message = f"{draft_message}{ending}"
            audio = generate_audio(text=message)
            if audio:
                context.bot.send_voice(chat_id=update.message.chat_id, voice=open(audio.name, 'rb'))
            else:
                context.bot.send_message(chat_id=update.message.chat_id, text="рвфцвьцфьтвоцфв")
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text=f'Попроси лучше{ending}')

    def bibametr_cmd(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=f"Твоя биба {random.randrange(3, 26)} сантиметров!")

    def help_cmd(self, update, context):
        commands = [
            self.SAY_CMD,
            self.BIBA_CMD,
            self.HELP_CMD,
            self.STATISTICS_CMD,
            self.SCREENSHOT_CMD,
        ]
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Умею и могу - {', '.join(commands)}")

    def statistics_cmd(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=f"Эти ублюдки мне должны:\n{self.statDao.get_all()}")

    def shutdown(self):
        self._updater.stop()
        self._updater.is_idle = False

    def screenshot_cmd(self, update, context):
        if len(context.args) == 1:
            url = context.args[0]
            screen = take_screenshot(url)
            if screen:
                context.bot.send_photo(
                    chat_id=update.message.chat_id,
                    photo=screen
                )
            else:
                context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text="Не могу сделать скрин."
                )
        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text="Не понял, повтори."
            )

    def secret_exit_cmd(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id, text="ня-пока")
        threading.Thread(target=self.shutdown).start()


def main():
    load_dotenv()

    bot = TelegramBot(
        token=os.getenv("TELEGRAM_BOT_TOKEN"),
        db_url=os.getenv("DB_URL")
    )
    bot.init_handlers()
    bot.start()


if __name__ == '__main__':
    main()
