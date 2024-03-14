from typing import Optional, Union
from bot.models.chat import Chat

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
            callback_id: Union[int, str, None] = None,
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
