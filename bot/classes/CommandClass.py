"""
Модуль, в котором объявляем все команды и привязку к конкретной функции
"""
from abc import ABC
from bot.classes.MainClass import Main
from bot.locks.all_locks import Locks


class Commands(Main, ABC):

    def distribute_commands(self, ):
        self.bot_commands = {

            # _______________   ОБЫЧНЫЕ ТЕКСТОВЫЕ СООБЩЕНИЯ БЕЗ ПАРАМЕТРОВ   _______________ #

            "message_commands": (
                {
                    "message": ("начать", "/start"),  # Важно прописывать все в нижнем регистре
                    "func": self.main_functions.example_func_without_params_with_extra,
                    "lock": Locks.classic,  # Необязательный параметр
                    "extra_params": "help param",  # Необязательный параметр
                },
            ),

            # _______________   ОБЫЧНЫЕ ТЕКСТОВЫЕ СООБЩЕНИЯ С ПАРАМЕТРОМ   _______________ #
            'message_commands_with_params': (
                {
                    "message": "меня зовут",
                    "func": self.main_functions.example_func_with_params,
                    # "lock": Locks.classic,
                    # "extra_params": "extra"
                },
            ),

            # _______________   ТЕКСТОВЫЕ СООБЩЕНИЯ С attachment   _______________ #

            'message_commands_with_attachment': (
                {
                    "message": ("смотри на мою фотку", "посмотри на мою фотку"),
                    "func": self.main_functions.example_func_with_attachment,
                    # "lock": Locks.classic,
                    # "extra_params": "extra"
                },
            ),

            # _______________   СООБЩЕНИЯ ТОЛЬКО С REPLY  _______________ #

            'message_commands_with_reply': (
                {
                    "message": "эй, друг",
                    "func": self.main_functions.example_func_only_with_reply,
                    # "lock": Locks.classic,
                    # "extra_params": "extra"
                },
            ),

            # _______________   СООБЩЕНИЯ CALLBACK  _______________ #

            "callback_messages": (
                {
                    "message": "test",
                    "func": self.main_functions.example_callback_func_without_params,
                    # "lock": Locks.classic,
                    # "extra_params": "extra"
                },
            ),

            # _______________   СООБЩЕНИЯ CALLBACK С ПАРАМЕТРАМИ  _______________ #

            'callback_messages_with_params': (
                {
                    "message": 'модерация',
                    "func": self.main_functions.example_callback_func_with_params,
                    # "lock": Locks.classic,
                    # "extra_params": "extra"
                },
            ),

        }
