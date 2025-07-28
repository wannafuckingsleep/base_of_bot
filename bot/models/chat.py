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

    @classmethod
    async def create_class(cls, row: dict) -> "Chat":
        """
        Создает объект класса на основе переданного словаря.

        :param row: Словарь с данными о чате (выгружаем из базы данных: таблица chat).
        :return: Объект класса Chat.
        """
        return Chat(
            chat_id=row["chat_id"],
            delete_message=row['delete_message'],
            start_date=row['start_date'],
            thread_id=row['thread_id'] if 'thread_id' in row else None,
        )
