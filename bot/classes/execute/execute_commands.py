import asyncio
from asyncio import CancelledError
from datetime import datetime
from typing import Optional, Union

from bot.objects.base_module import BaseModule
from bot.models.import_all_models import Message, Event
from bot.utils.keyboard.button import ButtonType, button


class ExecuteCommand(BaseModule):
    """
    Модуль команд бота.

    :param tb: Объект класса ToadBotMethods.
    :cvar tb: Объект класса ToadBotMethods.
    :cvar commands_count: Счётчик кол-ва команд для дневной статистики
    """
    commands_count: int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands_count = 0

    async def check_event_in_commands(
            self,
            event,
            command_list,
            with_params=False,
            clean_event_text: str = None
    ):  # -> Union[tuple[Event, dict], tuple[bool, bool]]:
        """
        Метод для проверки, есть ли сообщение в списке команд бота.

        :return: Объект Event с dict содержащим extra параметры или False при отсутствии.
        """
        for command in command_list:

            command_message = command['message']
            if with_params:
                if (
                    with_params and
                    type(command_message) is str and
                    event.startswith(command_message + " ")
                ):
                    return await self.bot.get_event_with_param(command_message, clean_event_text, command)

                elif with_params and type(command_message) is tuple:
                    for sub_command in command_message:

                        if not event.startswith(sub_command + " "):
                            continue

                        return await self.bot.get_event_with_param(sub_command, clean_event_text, command)

            else:
                if type(command_message) is str and command_message == event:
                    return await self.get_event_without_param(command, command_message)

                elif type(command_message) is tuple and event in command_message:
                    return await self.get_event_without_param(command, event)

        return False, False

    @staticmethod
    async def get_event_without_param(command, command_message) -> tuple:
        """
        Метод для получения объекта ивента без параметров.

        :return: Объект Event с dict содержащим extra параметры.
        """
        extra = {"func": command['func']}

        if 'extra_params' in command:
            extra['extra_params'] = command['extra_params']

        if 'lock' in command:
            extra['lock'] = command['lock']

        return Event(message=command_message), extra

    @staticmethod
    async def execute_method(event: Event,
                             command_data: dict) -> Optional[Message]:
        """
        Вызов метода с переданными параметрами

        :param event: Объект Event of platform
        :param command_data: Данные команды в виде dict из CommandClass
        """
        method = command_data['func']  # Получаем метод, который будет выполняться

        # Вызываем метод
        if 'extra_params' in command_data:
            message = await method(event, command_data['extra_params'])
        else:
            message = await method(event)

        return message

    async def execute_command(
            self,
            event: Event,
            command_dict: dict,
            log: str
    ):
        """
        Выполнение команд

        :param event: Объект Event of platform
        :param command_dict: Данные команды в виде dict из CommandClass
        :param log: Путь к файлу, куда писать лог
        """

        message: Optional[Union[Message, list[Message]]] = None
        event.chat = await self.bot.chat_settings.get(
            peer_id=event.chat_id,
            thread_id=event.thread_id,
            is_forum=event.is_forum
        )

        need_remove_lock = False  # Показывает необходимость снимать лок после завершения функции

        try:
            if 'lock' in command_dict:

                if event.chat_id in command_dict['lock'].queue:
                    message = Message(
                        event.chat_id,
                        command_dict['lock'].message
                    )

                else:
                    command_dict['lock'].queue[event.chat_id] = True
                    need_remove_lock = True

                    message = await self.execute_method(event, command_dict)

            else:
                message = await self.execute_method(event, command_dict)

            if message:

                self.bot.time_of_last_command = datetime.now()
                if type(message) is list:

                    sub_message: Message
                    for sub_message in message:
                        if type(sub_message) is not Message:
                            continue

                        if event.chat_id == sub_message.chat_id:
                            sub_message.chat = event.chat

                        await self.bot.send_message(sub_message)

                else:
                    if type(message) is Message:
                        if event.chat_id == message.chat_id:
                            message.chat = event.chat

                        await self.bot.send_message(message)

        except CancelledError:
            pass

        except Exception as e:
            result = e
            if message is not None:
                if type(message) is list:
                    result = " | ".join(str([i.__dict__ for i in message]))
                else:
                    result = message.__dict__

            log_message = (
                f"EventDict: {event.__dict__}\n"
                f"MessageDict: {result}\n"
            )
            await self.bot.write_log(
                log,
                log_message
            )

        finally:
            if need_remove_lock and event.chat_id in command_dict['lock'].queue:
                command_dict['lock'].queue.pop(event.chat_id)
