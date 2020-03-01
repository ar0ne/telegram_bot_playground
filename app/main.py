#!/usr/bin/env python
import os

import logging
import random
import re
import json

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from dotenv import load_dotenv
from functools import wraps
from typing import Callable, Any, TypeVar, cast

from app.dao.db import DataBaseConnector, UserDao, CommandDao, StatisticsDao
from app.extensions import dog_photo, cat_photo, text2speech, screenshoter

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

FuncType = Callable[..., Any]
F = TypeVar('F', bound=FuncType)  # pylint: disable=invalid-name


class TelegramBot:
    def __init__(self, token: str, db_url: str):
        assert token is not None, "Token must be not None"
        assert db_url is not None, "Database url must be not None"
        self._token = token
        self._updater = Updater(token=token, use_context=True)
        self._dispatcher = self._updater.dispatcher

        self.is_running = True  # since we use supervisor, we can't just turn off application

        self.SAY_CMD = 'say'
        self.BIBA_CMD = 'biba'
        self.PING_CMD = 'ping'
        self.HELP_CMD = 'help'
        self.WOOF_CMD = 'woof'
        self.MEOW_CMD = 'meow'
        self.STATISTICS_CMD = os.getenv('STATISTICS_COMMAND') or 'stat'
        self.EXIT_CMD = os.getenv('EXIT_COMMAND')
        self.SCREENSHOT_CMD = 'shot'

        self.db = DataBaseConnector(db_url)

        self.userDao = UserDao(self.db)
        self.cmdDao = CommandDao(self.db)
        self.statDao = StatisticsDao(self.db)

    def init_handlers(self):
        bibametr_handler = CommandHandler(self.BIBA_CMD, self.bibametr_cmd)
        ping_handler = CommandHandler(self.PING_CMD, self.ping_cmd)
        woof_handler = CommandHandler(self.WOOF_CMD, self.woof_cmd)
        meow_handler = CommandHandler(self.MEOW_CMD, self.meow_cmd)
        say_handler = CommandHandler(self.SAY_CMD, self.say_cmd)
        help_handler = CommandHandler(self.HELP_CMD, self.help_cmd)
        statistics_handler = CommandHandler(self.STATISTICS_CMD, self.statistics_cmd)
        unknown_handler = MessageHandler(Filters.command, self.unknown_cmd)
        secret_exit_handler = CommandHandler(self.EXIT_CMD, self.secret_exit_cmd)
        screenshot_handler = CommandHandler(self.SCREENSHOT_CMD, self.screenshot_cmd)

        self._dispatcher.add_handler(bibametr_handler)
        self._dispatcher.add_handler(ping_handler)
        self._dispatcher.add_handler(woof_handler)
        self._dispatcher.add_handler(meow_handler)
        self._dispatcher.add_handler(say_handler)
        self._dispatcher.add_handler(help_handler)
        self._dispatcher.add_handler(statistics_handler)
        self._dispatcher.add_handler(secret_exit_handler)
        self._dispatcher.add_handler(screenshot_handler)
        self._dispatcher.add_handler(unknown_handler)

    def start(self):
        self._updater.start_polling()
        self._updater.idle()

    def log_event(fn: F) -> F:
        @wraps(fn)
        def wrapped(self, *args, **kwargs):
            msg_text = args[0].message.text
            parsed_commands = re.findall(r"/(\w+)[ ]?", msg_text)
            command = None
            if len(parsed_commands) == 1:
                command = self.cmdDao.get_by_name(parsed_commands[0])

            if command:
                user_id = args[0].message.from_user.id
                user = self.userDao.get_by_id(user_id)

                if user:
                    self.statDao.increment(user['id'], command['id'])
                else:
                    self.userDao.add(
                        id=user_id,
                        username=args[0].message.from_user.username,
                        first_name=args[0].message.from_user.first_name,
                        last_name=args[0].message.from_user.last_name
                    )

            fn(self, *args, **kwargs)

        return cast(F, wrapped)

    def command(fn: F) -> F:
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            if self.is_running:
                fn(self, *args, **kwargs)

        return cast(F, wrapper)

    def unknown_cmd(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id, text="Твоя моя не пониматъ.")

    @command
    @log_event
    def say_cmd(self, update, context):
        ending = ', кожаный ублюдок!'
        draft_message = ' '.join(context.args).strip()
        if 0 < len(draft_message) < 250:
            message = f"{draft_message}{ending}"
            audio = text2speech.generate_audio(text=message)
            if audio:
                context.bot.send_voice(chat_id=update.message.chat_id, voice=open(audio.name, 'rb'))
                os.unlink(audio.name)
            else:
                context.bot.send_message(chat_id=update.message.chat_id, text="рвфцвьцфьтвоцфв")
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text=f'Попроси лучше{ending}')

    @command
    @log_event
    def bibametr_cmd(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=f"Твоя биба {random.randrange(3, 26)} сантиметров!")

    @command
    @log_event
    def help_cmd(self, update, context):
        commands = (
            self.SAY_CMD,
            self.BIBA_CMD,
            self.HELP_CMD,
            self.STATISTICS_CMD,
            self.SCREENSHOT_CMD,
            self.MEOW_CMD,
            self.WOOF_CMD,
            self.PING_CMD,
        )
        context.bot.send_message(
            chat_id=update.message.chat_id, text=f"Умею и могу - /{', /'.join(commands)}")

    @command
    @log_event
    def statistics_cmd(self, update, context):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"Твои должники:\n{json.dumps(self.statDao.get_all(), indent=4, sort_keys=True)}"
        )

    @command
    @log_event
    def screenshot_cmd(self, update, context):
        if len(context.args) == 1:
            url = context.args[0]
            screen = screenshoter.take_screenshot(url)
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

    @log_event
    def secret_exit_cmd(self, update, context):
        self.is_running = not self.is_running
        text = 'ня-пока' if not self.is_running else 'ня-привет'
        context.bot.send_message(chat_id=update.message.chat_id, text=text)

    @command
    @log_event
    def ping_cmd(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id, text="pong")

    @command
    @log_event
    def woof_cmd(self, update, context):
        context.bot.send_photo(chat_id=update.message.chat_id, photo=dog_photo.get_photo_url())

    @command
    @log_event
    def meow_cmd(self, update, context):
        context.bot.send_photo(chat_id=update.message.chat_id, photo=cat_photo.get_photo_url())


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
