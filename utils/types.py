from typing import Optional
from datetime import datetime


class Chat:
    """
        Объект чата
    """

    def __init__(
            self,
            peer_id: int,
            thread_id: Optional[int],
            delete_message: int,
            start_date: datetime,
    ):
        self.peer_id: int = peer_id
        self.thread_id: Optional[int] = thread_id  # Для использования бота в топиках
        self.delete_message: int = delete_message  # Поле для информации о автоудалении собщений
        self.start_date: datetime = start_date  # Дата добавления бота в чат


class Event:
    """
        Класс для удобного обращения к объектам ивента от платформ
    """

    def __init__(
            self,
            user_id: int = None,
            peer_id: int = None,
            username: Optional[str] = None,
            message: str = None,
            param: Optional[str] = None,
            attachment: Optional[str] = None,
            reply_from: Optional[str] = None,
            message_id: Optional[int] = None,
            callback_id: Optional[int] = None,
            destination: Optional[int] = None,
            is_bot: bool = None,
            chat: Optional[Chat] = None,
            thread_id: Optional[int] = None,
            is_forum: Optional[bool] = None,
    ):
        self.user_id: int = user_id
        self.peer_id: int = peer_id
        self.username: Optional[str] = username
        self.is_bot: bool = is_bot

        self.message: str = message
        self.param: Optional[str, None] = param
        self.attachment: Optional[str] = attachment
        self.chat: Optional[Chat] = chat
        self.thread_id: Optional[int] = thread_id

        self.reply_from: Optional[int, None] = reply_from
        self.destination: Optional[int] = destination

        self.message_id: Optional[int, None] = message_id
        self.callback_id: Optional[int, None] = callback_id

        self.is_forum: Optional[bool] = is_forum
