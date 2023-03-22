from typing import Optional
from datetime import datetime
from vkbottle import Keyboard as VkKeyboard
from aiogram.types import InlineKeyboardMarkup


class Chat:
    """
        Объект чата
    """

    def __init__(
            self,
            chat_id: int,
            thread_id: Optional[int],
            delete_message: int,
            start_date: datetime,
    ):
        self.chat_id: int = chat_id
        self.thread_id: Optional[int] = thread_id  # Для использования бота в топиках
        self.delete_message: int = delete_message  # число в минутах, после которого нужно удалять сообщения
        self.start_date: datetime = start_date  # Дата добавления бота в чат


class Event:
    """
        Класс для удобного обращения к объектам ивента от платформ
    """

    def __init__(
            self,
            user_id: int = None,
            chat_id: int = None,
            username: Optional[str] = None,
            message: Optional[str] = None,
            param: Optional[str] = None,
            attachment: Optional[str] = None,
            reply_from: Optional[int] = None,
            message_id: Optional[int] = None,
            callback_id: Optional[int] = None,
            destination: Optional[int] = None,
            is_bot: bool = None,
            chat: Optional[Chat] = None,
            thread_id: Optional[int] = None,
            is_forum: Optional[bool] = None,
    ):
        self.user_id: int = user_id
        self.chat_id: int = chat_id
        self.username: Optional[str] = username
        self.is_bot: bool = is_bot

        self.message = message
        self.param = param
        self.attachment = attachment
        self.chat = chat
        self.thread_id = thread_id

        self.reply_from = reply_from
        self.destination = destination

        self.message_id = message_id
        self.callback_id = callback_id

        self.is_forum = is_forum


class Message:

    def __init__(self,
                 chat_id: int,
                 message: str,
                 current_chat: Optional[Chat] = None,
                 thread_id: Optional[int] = None,
                 attachment: Optional[str] = None,
                 keyboard: Optional[list, InlineKeyboardMarkup, VkKeyboard] = None,
                 ping: bool = False,
                 message_type: str = "text",
                 need_log: bool = True,
                 need_exception: bool = False,
                 dont_parse_links: int = 1,
                 need_delete: bool = True,
                 message_id: Optional[int] = None,
                 callback_id: Optional[int] = None,
                 ):
        self.chat_id = chat_id
        self.message = message
        self.thread_id = thread_id
        self.current_chat = current_chat

        self.attachment = attachment
        self.keyboard = keyboard
        self.ping = ping
        self.message_type = message_type
        self.need_log = need_log
        self.need_exception = need_exception
        self.dont_parse_links = dont_parse_links
        self.need_delete = need_delete
        self.message_id = message_id
        self.callback_id = callback_id
