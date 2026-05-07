import typing
from datetime import datetime, timedelta

from bot.objects.base_module import BaseModule
from bot.objects.emojies import Emoji
from bot.models.import_all_models import Chat, Event, Message


class ChatSettings(BaseModule):
    """
    Модуль настроек чата.

    :param bot: Объект класса ToadBotMethods.
    :cvar bot: Объект класса ToadBotMethods.
    """

    async def get(
            self,
            peer_id: int,
            thread_id: typing.Optional[None] = None,
            update_data: bool = False
    ) -> Chat:
        """
        Получить информацию и настройки текущего чата

        :param peer_id: ChatID.
        :param thread_id: Передавать значение для обновления actual topic (для работы с топиками в ТГ).
        :param update_data: Нужно ли получить актуальные данные чата из БД и вернуть объект со значениями из базы.
        :return: Object of the Chat
        """
        # Если передают не чат, то возвращаем *костыль*
        if not await self.bot.is_chat(peer_id):
            return Chat(
                peer_id,
                thread_id=None,
                delete_message=-1,
                start_date=datetime.now()
            )

        if update_data:
            self.bot.chats_data[peer_id] = await self._get_actual_chat_data(peer_id, thread_id)

        try:
            chat = self.bot.chats_data[peer_id]
        except KeyError:
            self.bot.chats_data[peer_id] = await self._get_actual_chat_data(peer_id, thread_id)
            chat = self.bot.chats_data[peer_id]

        return chat

    async def _create_chat(self,
                           peer_id: int,
                           thread_id: typing.Optional[None] = None) -> Chat:
        """
        Создание записи чата в БД, если ее нет.
        :param peer_id: ChatID.
        :param thread_id: Передавать значение для обновления actual topic (для работы с топиками в ТГ)
        :return: Объект класса Chat.
        """
        await self.bot.db.execute(
            """
            INSERT IGNORE INTO chat SET chat_id = %s, start_date = NOW();
            """,
            (peer_id, ),
            commit=True)

        return Chat(
            peer_id,
            delete_message=-1,
            start_date=datetime.now(),
            thread_id=thread_id,
        )

    async def _get_actual_chat_data(self,
                                    peer_id: int,
                                    thread_id: typing.Optional[None] = None) -> Chat:
        """
        Получает актуальные данные чата из БД.
        :param peer_id: ChatID.
        :param thread_id: Передавать значение для обновления actual topic (для работы с топиками в ТГ).
        :return: Объект класса Chat.
        """
        is_chat_exist = await self.bot.db.execute("SELECT * FROM chat WHERE chat_id = %s",
                                                 (peer_id, ),
                                                 fetchone=True)
        if is_chat_exist:
            return await Chat.create_class(is_chat_exist)
        else:
            return await self._create_chat(peer_id, thread_id)
