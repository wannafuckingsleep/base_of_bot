from typing import Optional, Union

from bot.models.chat import Chat

class Message:
    def __init__(
            self,
            chat_id: int,
            message: str,
            chat: Optional[Chat] = None,
            thread_id: Optional[int] = None,
            attachment: Optional[str] = None,
            keyboard: Union[list, None] = None,
            ping: bool = False,
            message_type: str = "text",
            need_log: bool = True,
            need_exception: bool = False,
            web_page_preview: bool = False,  # Предпоказ ссылок в сообщении
            dont_parse_links: int = 1,
            need_delete: bool = True,
            message_id: Optional[int] = None,
            callback_id: Union[int, str, None] = None,
            user_id: Optional[int] = None,
            reply_to_message_id: int = None  # message_id to reply message
    ):
        self.chat_id = chat_id
        self.message = message
        self.thread_id = thread_id
        self.chat = chat

        self.attachment = attachment
        self.keyboard = keyboard
        self.ping = ping
        self.message_type = message_type
        self.need_log = need_log
        self.need_exception = need_exception
        self.web_page_preview = web_page_preview
        self.dont_parse_links = dont_parse_links
        self.need_delete = need_delete
        self.message_id = message_id
        self.callback_id = callback_id
        self.reply_to_message_id = reply_to_message_id

        self.user_id = user_id
