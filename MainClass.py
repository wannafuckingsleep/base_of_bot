import asyncio
import nest_asyncio
from abc import abstractmethod
from DBClass import DBClass
import re
import os
import traceback
from datetime import timedelta

from asyncio import CancelledError
import aiofiles

from utils.keyboards import Keyboard
from utils.types import *
from settings import product_server, log_dir
from migrations import check_migrations

nest_asyncio.apply()


# Родительский класс с объявлением всех стартовых для работы методов
class Main:

    keyboard: Keyboard  # Класс с клавиатурами бота
    db: Optional[DBClass] = None  # БД
    bot_commands: dict  # Словарь с коммандами бота

    admins: tuple[int]  # Список UserID админов.

    # Лок, который блокирует одновременное выполнение одинаковых команд в одном чате.
    # Используется в CommandClass.py
    command_lock: dict = {
        "queue": {},
        "message": "Попробуйте использовать команду через 5 секунд"  # Текст, который будет выдавать лок
    }

    delete_queue: Optional[asyncio.Queue] = None  # Используется для автоудаления сообщений
    subscribed_chats: dict = {}  # Подписанные чаты на автоудаление сообщений
    need_delete: dict = {}

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

    async def on_startup(self):  # Асинхронная функция, выполняющаяся перед стартом получения апдейтов
        self.delete_queue = asyncio.Queue()
        await self.mysql_connect()
        await check_migrations(self.db)  # Выполняем миграции
        await self.get_keyboards()
        asyncio.create_task(self.check_for_delete())
        asyncio.create_task(self.delete_messages())
        asyncio.create_task(self.get_subscribed_chats())
        if product_server:
            for admin in self.admins:
                await self.send_message(Message(admin, "SendEvents start", need_delete=False))

    # Перезагрузка бота
    async def reboot(self, user):
        await self.mysql_disconnect()
        for admin in self.admins:
            await self.send_message(Message(admin, 'rebooted by ' + str(user)))
        await asyncio.sleep(1)
        os._exit(1)

    # Асинхронная функция, выполняющаяся после прекращения получения апдейтов
    async def on_shutdown(self):
        await self.mysql_disconnect()

    @abstractmethod  # Отправляем сообщение
    async def send_message(self, message: Message):
        ...

    @abstractmethod  # Удаляем сообщение
    async def delete_message(self, message: Message):
        ...

    @abstractmethod  # Правка сообщения
    async def edit_message(self, message: Message):
        ...

    @abstractmethod  # Callback ответ
    async def callback_message(self, message: Message, alert=True):
        ...

    @classmethod
    @abstractmethod
    async def get_message_id(cls, message) -> Optional[int]: # Получение ID отправленного сообщения
        ...

    @property
    @abstractmethod
    def base(self):  # Имя БД
        pass

    @property
    @abstractmethod
    def platform(self):  # TODO Название платформы, нужно в будущем отказаться
        pass

    @classmethod
    async def write_log(cls, filename, error_text, need_print=False):  # Запись лога об ошибке
        if need_print or not product_server:
            print(error_text)
        else:
            async with aiofiles.open(f'{log_dir}/{filename}.txt', 'a') as file:
                error_text = f'{str(datetime.now())}\n{error_text}'
                await file.write(error_text)
                await file.flush()

    # Добавляем сообщение в очередь на удаление
    async def message_for_delete(self, message_id, peer_id):
        await self.delete_queue.put(
            {'peer_id': peer_id, 'message': message_id, 'platform': self.platform, 'date': datetime.now()})

    # Поток раз в 1.5 минут получает чаты, подписанные на удаление
    async def get_subscribed_chats(self):
        while True:
            try:
                rows = await self.db.execute("SELECT delete_message, peer_id FROM chat WHERE delete_message != -1",
                                             fetchall=True)
                self.subscribed_chats.clear()
                for row in rows:
                    peer_id = row['peer_id']
                    time = row['delete_message']
                    self.subscribed_chats[peer_id] = time
                del rows
                await asyncio.sleep(100)
            except CancelledError:
                raise
            except:
                await Main.write_log('delete_message_log', traceback.format_exc())

    # Поток принимает отправленные ботом сообщения, и смотрит, подписана ли беседа на удаление сообщений
    # Если подписана, значит отправляет в очередь на удаление
    async def check_for_delete(self):
        while True:
            try:
                event = await self.delete_queue.get()  # comment event
                peer_id = event['peer_id']
                if peer_id in self.subscribed_chats:
                    event['time'] = self.subscribed_chats.copy()[peer_id]
                    message_id = event['message']
                    self.need_delete[message_id] = event
            except CancelledError:
                raise
            except:
                await Main.write_log('delete_message_log', traceback.format_exc())

    # Поток удаляет сообщения по истечению нужного времени
    async def delete_messages(self):
        while True:
            try:
                if len(self.need_delete) > 0:
                    for key in list(self.need_delete):
                        event = self.need_delete[key]
                        peer_id = event['peer_id']
                        date = event['date']
                        message_id = event['message']
                        minute = event['time']
                        today = datetime.now()
                        if today - timedelta(minutes=minute) >= date:
                            await self.delete_message(
                                Message(peer_id, message="", message_id=message_id)
                            )
                            self.need_delete.pop(message_id)

                await asyncio.sleep(30)
            except CancelledError:
                raise
            except:
                await Main.write_log('delete_message_log', traceback.format_exc())
