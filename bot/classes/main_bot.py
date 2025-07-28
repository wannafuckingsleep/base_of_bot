import asyncio
import nest_asyncio
from abc import abstractmethod, ABC
import re
import os
import traceback
from datetime import datetime, timedelta

from asyncio import CancelledError
import aiofiles

from bot.classes.battles.battle import Battle
from bot.classes.chat_settings.chat_settings_logic import ChatSettings
from bot.utils.keyboard.keyboard import Keyboard

from typing import Union, Optional
import aiohttp

from settings import product_server, log_dir
from bot.modules.migrations import check_migrations
from bot.utils.images import Images
from bot.classes.DBClass import DBClass

from bot.models.import_all_models import *
from bot.classes.example_functions import ExampleFuncs

nest_asyncio.apply()


# Родительский класс с объявлением всех стартовых для работы методов
class Main(ABC):
    """
    Основной класс бота со всем нужным функционалом и инициализированными модулями (в __init__)

    :cvar keyboard: Keyboard object.
    :cvar db: DB object.
    """

    keyboard: Keyboard  # Класс с клавиатурами бота
    db: Optional[DBClass] = None  # БД
    bot_commands: dict  # Словарь с коммандами бота
    image: Images

    admins: tuple[int]  # Список UserID админов.

    chats_data: dict = {}

    # Объявляем наличие функциональных модулей, к которым у нас будет доступно обращение.
    example_functions: ExampleFuncs
    battle: Battle

    def __init__(self):
        # При создании новых функциональных модулей, добавлять инициализацию в текущий конструктор
        self.example_functions = ExampleFuncs(self)
        self.battle = Battle(self)  # Пример построенной цепочки классов: бой -> подземелье и т.д. Battle -> Dungeon
        self.chat_settings = ChatSettings(self)

    # Индивидуальная генерация клавиатуры для отдельной платформы
    @abstractmethod
    async def generate_keyboard(self, buttons):
        pass

    # Конечное формирование клавиатуры
    async def get_keyboards(self):
        keyboard = Keyboard()

        for attribute in dir(keyboard):
            if attribute.startswith("_"):
                continue

            value = getattr(keyboard, attribute)
            setattr(
                keyboard,
                attribute,
                await self.generate_keyboard(value)
            )

        self.keyboard = keyboard

    async def mysql_connect(self, self_class=True):
        db = DBClass()
        await db.mysql_connect(self.base)

        if self_class:
            self.db = db
            return

        return db

    async def mysql_disconnect(self, db=None):
        if db is None:
            db = self.db

        if db is not None:
            await db.mysql_disconnect()

    @staticmethod
    async def get_event_with_param(command_message, clean_event_text, command) -> tuple:
        param = re.sub(
            re.escape(command_message + ' '), '',
            clean_event_text,
            flags=re.IGNORECASE
        )

        extra = {"func": command['func']}
        if 'extra_params' in command:
            extra['extra_params'] = command['extra_params']

        if 'lock' in command:
            extra['lock'] = command['lock']

        return (Event(message=command_message,
                      param=param),
                extra)

    @staticmethod
    async def get_event_without_param(command, command_message) -> tuple:
        extra = {"func": command['func']}

        if 'extra_params' in command:
            extra['extra_params'] = command['extra_params']

        if 'lock' in command:
            extra['lock'] = command['lock']

        return Event(message=command_message), extra

    # Проверяем, есть ли сообщение в списке команд бота
    async def check_event_in_commands(
            self,
            event,
            command_list,
            with_params=False,
            clean_event_text: str = None
    ):  # -> Union[tuple[Event, dict], tuple[bool, bool]]:
        for command in command_list:

            command_message = command['message']
            if with_params:
                if (
                    with_params and
                    type(command_message) == str and
                    event.startswith(command_message + " ")
                ):
                    return await self.get_event_with_param(command_message, clean_event_text, command)

                elif with_params and type(command_message) == tuple:
                    for sub_command in command_message:

                        if not event.startswith(sub_command + " "):
                            continue

                        return await self.get_event_with_param(sub_command, clean_event_text, command)

            else:
                if type(command_message) == str and command_message == event:
                    return await self.get_event_without_param(command, command_message)

                elif type(command_message) == tuple and event in command_message:
                    return await self.get_event_without_param(command, event)

        return False, False

    async def on_startup(self):  # Асинхронная функция, выполняющаяся перед стартом получения апдейтов
        await self.mysql_connect()
        await check_migrations(self.db)  # Выполняем миграции
        await self.get_keyboards()

        if product_server:
            for admin in self.admins:
                await self.send_message(
                    Message(
                        admin,
                        "SendEvents start",
                        need_delete=False
                    )
                )

    # Асинхронная функция, выполняющаяся после прекращения получения апдейтов
    async def on_shutdown(self):
        await self.mysql_disconnect()

    @abstractmethod  # Отправляем сообщение
    async def send_message(self, message: Message): ...

    @abstractmethod  # Удаляем сообщение
    async def delete_message(self, message: Message): ...

    @abstractmethod  # Правка сообщения
    async def edit_message(self, message: Message): ...

    @abstractmethod  # Callback ответ
    async def callback_message(self, message: Message, alert=True): ...

    @classmethod
    @abstractmethod
    async def get_message_id(cls, message) -> Optional[int]: ...  # Получение ID отправленного сообщения

    @property
    @abstractmethod
    def base(self):  # Имя БД
        pass

    @property
    @abstractmethod
    def platform(self):  # TODO Название платформы, нужно в будущем отказаться
        pass

    @abstractmethod
    async def is_chat(self, chat_id: int) -> bool: ...

    @abstractmethod
    # Получение юзера человека, с которым нужно будет взаимодействовать
    async def get_destination(self, param, reply_from): ...

    @abstractmethod
    async def is_admin(self, user_id: int, chat_id: int) -> bool: ...  # Является ли пользователь админом

    @abstractmethod
    async def escape_string(self, s: str) -> str: ...  # Экранирование строки

    @staticmethod
    @abstractmethod
    async def make_link(title: str, link): ...  # Формируем ссылку

    @staticmethod
    @abstractmethod
    async def link_to_user(user_id: int): ...  # Получаем ссылку на пользователя

    @staticmethod
    @abstractmethod
    async def bold(s): ...  # Делаем текст жирным

    @staticmethod
    @abstractmethod
    async def italic(s): ...  # Делаем текст курсивом

    @staticmethod
    @abstractmethod
    async def underline(s): ...  # Делаем текст подчеркнутым

    @staticmethod
    @abstractmethod
    async def code(s): ...  # Делаем текст monospace

    @abstractmethod
    async def get_name(self, user_id: int, chat_id: int,
                       ping: bool = False,
                       special_name: Optional[str] = None) -> Optional[str]: ...

    @abstractmethod
    async def get_attachment_id(self, event, need_all=False): ...  # Получаем id вложения

    @staticmethod
    async def is_int(s):  # Проверка целочисленности
        try:
            s = int(s)
            return s

        except ValueError:
            return False

    @classmethod
    async def write_log(cls, filename, error_text, need_print=False):  # Запись лога об ошибке
        if need_print or not product_server:
            print(error_text)
            return

        async with aiofiles.open(f'{log_dir}/{filename}.txt', 'a') as file:
            error_text = f'{str(datetime.now())}\n{error_text}'
            await file.write(error_text)
            await file.flush()

    # Перемещаем чат
    async def chat_migrate(self, from_chat_id, to_chat_id):
        await self.db.execute(
            """
                UPDATE chat SET chat_id = %s 
                    WHERE chat_id = %s;
            """,
            ( to_chat_id, from_chat_id ),
            commit=True
        )

    # Обработка ошибок отправки сообщений
    # TODO Вынести текст сообщения про ошибки в свойства класса, оставить только общую функцию
    @staticmethod
    async def write_msg_errors(err):
        err = "{0}".format(err)
        # Бота кикнули, запретили ему присылать фото и т.д.
        if (err.find('bot was kicked from the') >= 0 or err.find('chat was deactivated') >= 0
                or err.find('bot is not a member') >= 0 or err.find('no rights to send') >= 0
                or err.find('enough rights to send photos') >= 0
                or err.find('Chat not found') >= 0
                or err == '7' or err == '945'):
            return 'kicked'
        else:
            # Неизвестная пока для нас ошибка.
            # Может нужно лог завести, чтобы все возникающие ошибки обработать
            return 'unknown'

    @staticmethod
    async def download_file(url: str) -> Union[bytes, bool]:
        """
        Download file

        :param url: address of file
        :return: False or bytes
        """
        async with aiohttp.ClientSession() as session:

            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.read()

                else:
                    return False

    async def hello(self, event: Event):
        print("hello from Main-hello()")
