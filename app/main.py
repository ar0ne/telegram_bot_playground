#!/usr/bin/env python
import os
import logging
import random
import re
import json

from typing import Callable, Any, TypeVar, cast
from dotenv import load_dotenv
from functools import wraps
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from dao.db import DataBaseConnector, UserDao, CommandDao, StatisticsDao
from extensions import dog_photo, cat_photo, text2speech, screenshoter

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

FuncType = Callable[..., Any]
F = TypeVar('F', bound=FuncType)  # pylint: disable=invalid-name


class TelegramBot:
    def __init__(self, token: str, db_url: str):
        assert token, "Token must be not None"
        assert db_url, "Database url must be not None"
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
        self.STATISTICS_CMD = os.getenv('STATISTICS_COMMAND', 'stat')
        self.EXIT_CMD = os.getenv('EXIT_COMMAND', 'bye')
        self.SCREENSHOT_CMD = 'shot'

        self.db = DataBaseConnector(db_url)

        self.user_dao = UserDao(self.db)
        self.cmd_dao = CommandDao(self.db)
        self.statistic_dao = StatisticsDao(self.db)

    def init_handlers(self):
        for handler in (
                CommandHandler(self.BIBA_CMD, self.bibametr_cmd),
                CommandHandler(self.PING_CMD, self.ping_cmd),
                CommandHandler(self.WOOF_CMD, self.woof_cmd),
                CommandHandler(self.MEOW_CMD, self.meow_cmd),
                CommandHandler(self.SAY_CMD, self.say_cmd),
                CommandHandler(self.HELP_CMD, self.help_cmd),
                CommandHandler(self.STATISTICS_CMD, self.statistics_cmd),
                CommandHandler(self.EXIT_CMD, self.secret_exit_cmd),
                CommandHandler(self.SCREENSHOT_CMD, self.screenshot_cmd),
                MessageHandler(Filters.command, self.unknown_cmd),
        ):
            self._dispatcher.add_handler(handler)

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
                command = self.cmd_dao.get_by_name(parsed_commands[0])

            if command:
                user_id = args[0].message.from_user.id
                user = self.user_dao.get_by_id(user_id)

                if user:
                    self.statistic_dao.increment(user['id'], command['id'])
                else:
                    self.user_dao.add(
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
            text=f"Твои должники:\n"
            f"{json.dumps(self.statistic_dao.get_all(), indent=4, sort_keys=True)}"
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
        token=os.getenv("TELEGRAM_BOT_TOKEN", ''),
        db_url=os.getenv("DB_URL", 'sqlite:///:memory:')
    )
    bot.init_handlers()
    bot.start()


if __name__ == '__main__':
    main()
