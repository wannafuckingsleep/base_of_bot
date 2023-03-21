import asyncio
import nest_asyncio
from abc import abstractmethod
from DBClass import DBClass
from typing import Optional
import re

from utils.keyboards import Keyboard

nest_asyncio.apply()


class Main:

    keyboard: Keyboard
    db: Optional[DBClass] = None
    bot_commands: dict

    # Лок, который блокирует одновременное выполнение одинаковых команд в одном чате.
    # Используется в CommandClass.py
    command_lock: dict = {
        "queue": {},
        "message": "Попробуйте использовать команду через 5 секунд"  # Текст, который будет выдавать лок
    }

    def __init__(self):
        pass

    # Индивидуальная генерация клавиатуры для отдельной платформы
    @abstractmethod
    async def generate_keyboard(self, buttons):
        pass

    # Конечное формирование клавиатуры
    async def get_keyboards(self):
        keyboard = Keyboard()
        for attribute in dir(keyboard):
            if not attribute.startswith("__"):
                value = getattr(keyboard, attribute)
                setattr(keyboard, attribute,
                        await self.generate_keyboard(
                            value
                        ))
        self.keyboard = keyboard

    async def mysql_connect(self, self_class=True):
        db = DBClass()
        await db.mysql_connect(self.base)

        if self_class:
            self.db = db
        else:
            return db

    async def mysql_disconnect(self, db=None):
        if db is None:
            db = self.db
        if db is not None:
            await db.mysql_disconnect()

    # Проверяем, есть ли сообщение в списке команд бота
    @staticmethod
    async def check_event_in_commands(event, command_list, with_params=False,
                                      clean_event_text: str = None):  # -> Union[tuple[Event, dict], tuple[bool, bool]]:
        for command in command_list:
            command_message = command['message']
            if with_params:
                if with_params and type(command_message) == str and event.startswith(command_message + " "):
                    param = re.sub(re.escape(command_message + ' '), '', clean_event_text, flags=re.IGNORECASE)
                    extra = {"func": command['func']}
                    if 'extra_params' in command:
                        extra['extra_params'] = command['extra_params']
                    if 'lock' in command:
                        extra['lock'] = command['lock']
                    return Event(message=command_message, param=param), extra
                elif with_params and type(command_message) == tuple:
                    for sub_command in command_message:
                        if event.startswith(sub_command + " "):
                            param = re.sub(re.escape(sub_command + ' '), '', clean_event_text, flags=re.IGNORECASE)
                            extra = {"func": command['func']}
                            if 'extra_params' in command:
                                extra['extra_params'] = command['extra_params']
                            if 'lock' in command:
                                extra['lock'] = command['lock']
                            return Event(message=event, param=param), extra
            else:
                if type(command_message) == str and command_message == event:
                    extra = {"func": command['func']}
                    if 'extra_params' in command:
                        extra['extra_params'] = command['extra_params']
                    if 'lock' in command:
                        extra['lock'] = command['lock']
                    return Event(message=command_message), extra
                elif type(command_message) == tuple:
                    if event in command_message:
                        extra = {"func": command['func']}
                        if 'extra_params' in command:
                            extra['extra_params'] = command['extra_params']
                        if 'lock' in command:
                            extra['lock'] = command['lock']
                        return Event(message=event), extra
        if with_params:
            return False, False
        else:
            return False, False

    @property
    @abstractmethod
    def base(self):  # Имя БД
        pass
