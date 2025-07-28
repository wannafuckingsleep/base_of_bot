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
    # Число часов, в течение которых новый чат может брать жаб бесконечно
    infinity_toads_time = 24

    async def get(
            self,
            peer_id: int,
            thread_id: typing.Optional[None] = None,
            is_forum=None,
            update_data: bool = False
    ) -> Chat:
        """
        Получить информацию и настройки текущего чата

        :param peer_id: ChatID.
        :param thread_id: Передавать значение для обновления actual topic (для работы с топиками в ТГ).
        :param is_forum: Включены ли топики в чате.
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

        if chat.is_topic_lock == 0:
            if is_forum:
                if chat.thread_id != thread_id:
                    await self.bot.db.execute("UPDATE chat SET thread_id = %s WHERE chat_id = %s", (thread_id, peer_id), commit=True)
                    chat.thread_id = thread_id

            elif is_forum is False and chat.thread_id:
                await self.bot.db.execute("UPDATE chat SET thread_id = NULL WHERE chat_id = %s", (peer_id,), commit=True)
                chat.thread_id = None

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
        # Если в чате есть жабки, значит включаем бесконечных жабок на определенный срок
        toads = await self.bot.db.execute(f"SELECT user_id FROM toads WHERE peer_id = {peer_id} limit 1",
                                         fetchone=True)
        time = datetime.now()
        if toads:
            time -= timedelta(hours=self.infinity_toads_time + 1)

        await self.bot.db.execute(
            """
            INSERT IGNORE INTO chat SET chat_id = %s, start_date = %s;
            """,
            (peer_id, time),
            commit=True)

        return Chat(
            peer_id,
            delete_message=-1,
            start_date=time,
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
