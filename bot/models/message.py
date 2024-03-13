from typing import Optional, Union

from vkbottle import Keyboard as VkKeyboard
from aiogram.types import InlineKeyboardMarkup

from bot.models.chat import Chat

class Message:
    def __init__(
            self,
            chat_id: int,
            message: str,
            current_chat: Optional[Chat] = None,
            thread_id: Optional[int] = None,
            attachment: Optional[str] = None,
            keyboard: Union[list, InlineKeyboardMarkup, VkKeyboard, None] = None,
            ping: bool = False,
            message_type: str = "text",
            need_log: bool = True,
            need_exception: bool = False,
            dont_parse_links: int = 1,
            need_delete: bool = True,
            message_id: Optional[int] = None,
            callback_id: Union[int, str, None] = None,
            user_id: Optional[int] = None,
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

        self.user_id = user_id