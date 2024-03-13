from typing import Optional
from datetime import datetime

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