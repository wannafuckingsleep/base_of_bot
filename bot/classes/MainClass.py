import asyncio
import nest_asyncio
from abc import abstractmethod
from bot.classes.DBClass import DBClass
import re
import os
import traceback
from datetime import timedelta

from asyncio import CancelledError
import aiofiles

from bot.utils.keyboards import Keyboard
from bot.utils.types import *
from typing import Union
import aiohttp
from settings import product_server, log_dir
from bot.modules.migrations import check_migrations
from bot.utils.images import Images

nest_asyncio.apply()


# Родительский класс с объявлением всех стартовых для работы методов
class Main:

    keyboard: Keyboard  # Класс с клавиатурами бота
    db: Optional[DBClass] = None  # БД
    bot_commands: dict  # Словарь с коммандами бота
    image: Images

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
                                      clean_event_text: str = None) -> Union[tuple[Event, dict], tuple[bool, bool]]:
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
        
    async def execute_command(self, event: Event, extra: dict, log: str):
        message: Optional[Message, list[Message]] = None
        event.chat = await self.get_chat_settings(
            chat_id=event.chat_id,
            thread_id=event.thread_id,
            is_forum=event.is_forum
        )
        try:
            if 'lock' in extra:
                try:
                    if event.chat_id in extra['lock']['queue']:
                        message = Message(event.chat_id, extra['lock']['message'])
                    else:
                        try:

                            extra['lock']['queue'][event.chat_id] = True
                            if 'extra_params' in extra:
                                message = await extra['func'](event, extra['extra_params'])
                            else:
                                message = await extra['func'](event)
                        except:
                            await self.write_log(log, "\n"
                                                      "_" * 25 + f'\n{datetime.now()}\n'
                                                                 f'{event.__dict__}\n'
                                                                 f'{traceback.format_exc()}')
                        finally:
                            if event.chat_id in extra['lock']['queue']:
                                extra['lock']['queue'].pop(event.chat_id)  # Разблокируем команды очереди
                except:
                    await self.write_log(log, "\n"
                                              "_" * 25 + f'\n{datetime.now()}\n'
                                                         f'{event.__dict__}\n'
                                                         f'{traceback.format_exc()}')
            else:
                if 'extra_params' in extra:
                    message = await extra['func'](event, extra['extra_params'])
                else:
                    message = await extra['func'](event)
            if message:
                if type(message) == list:
                    for current_message in message:
                        if type(current_message) == Message:
                            if event.chat_id == current_message.chat_id:
                                current_message.chat = event.chat
                            await self.send_message(current_message)
                            await asyncio.sleep(0.1)
                else:
                    if type(message) == Message:
                        if event.chat_id == message.chat_id:
                            message.chat = event.chat
                        await self.send_message(message)
        except:
            result = ""
            if message is not None:
                if type(message) == list:
                    for i in message:
                        result += f"\n\n{i.__dict__}"
                else:
                    result += f"\n\n{message.__dict__}"

            await self.write_log(log, "_" * 25 +
                                 f"\n{event.__dict__}{result}\n" + traceback.format_exc() + "_" * 25)

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

    async def get_chat_settings(self, chat_id: int, db: DBClass = None, thread_id=None, is_forum=None) -> Chat:
        if not await self.is_chat(chat_id):
            return Chat(chat_id, thread_id=None, delete_message=-1, start_date=datetime.now())
        if db is None:
            db = self.db
        chat = await db.execute("SELECT * FROM chat WHERE chat_id = %s", (chat_id,), fetchone=True)
        if chat is None:
            await db.execute("INSERT INTO chat SET chat_id = %s, start_date = %s",
                             (chat_id, datetime.now()), commit=True)
            chat = await db.execute("SELECT * FROM chat WHERE chat_id = %s", (chat_id,), fetchone=True)
        if is_forum:
            if chat['thread_id'] != thread_id:
                await db.execute("UPDATE chat SET thread_id = %s WHERE chat_id = %s", (thread_id, chat_id), commit=True)
                chat['thread_id'] = thread_id
        elif is_forum is False and chat['thread_id']:
            await db.execute("UPDATE chat SET thread_id = NULL WHERE chat_id = %s", (chat_id,), commit=True)
            chat['thread_id'] = None

        return Chat(
            chat_id, thread_id=chat['thread_id'], delete_message=chat['delete_message'], start_date=chat['start_date']
        )

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

    @classmethod
    async def write_log(cls, filename, error_text, need_print=False):  # Запись лога об ошибке
        if need_print or not product_server:
            print(error_text)
        else:
            async with aiofiles.open(f'{log_dir}/{filename}.txt', 'a') as file:
                error_text = f'{str(datetime.now())}\n{error_text}'
                await file.write(error_text)
                await file.flush()

    # Перемещаем чат
    async def chat_migrate(self, from_chat_id, to_chat_id):
        await self.db.execute("""
            UPDATE chat SET chat_id = %s WHERE chat_id = %s;
        """, (
            to_chat_id, from_chat_id
        ), commit=True)

    # Обработка ошибок отправки сообщений
    # TODO Вынести текст сообщения про ошибки в свойства класса, оставить только общую функцию
    async def write_msg_errors(self, err, chat_id):
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

    # Добавляем сообщение в очередь на удаление
    async def message_for_delete(self, message_id, chat_id):
        await self.delete_queue.put(
            {'chat_id': chat_id, 'message': message_id, 'platform': self.platform, 'date': datetime.now()})

    # Поток раз в 1.5 минут получает чаты, подписанные на удаление
    async def get_subscribed_chats(self):
        while True:
            try:
                rows = await self.db.execute("SELECT delete_message, chat_id FROM chat WHERE delete_message != -1",
                                             fetchall=True)
                self.subscribed_chats.clear()
                for row in rows:
                    chat_id = row['chat_id']
                    time = row['delete_message']
                    self.subscribed_chats[chat_id] = time
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
                chat_id = event['chat_id']
                if chat_id in self.subscribed_chats:
                    event['time'] = self.subscribed_chats.copy()[chat_id]
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
                        chat_id = event['chat_id']
                        date = event['date']
                        message_id = event['message']
                        minute = event['time']
                        today = datetime.now()
                        if today - timedelta(minutes=minute) >= date:
                            await self.delete_message(
                                Message(chat_id, message="", message_id=message_id)
                            )
                            self.need_delete.pop(message_id)

                await asyncio.sleep(30)
            except CancelledError:
                raise
            except:
                await Main.write_log('delete_message_log', traceback.format_exc())

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
