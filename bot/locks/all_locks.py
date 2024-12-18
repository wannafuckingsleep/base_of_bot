"""
Модуль со всеми "блокировщиками", которые блокируют множественное выполнение асинхронных функций в конкретном чате.
"""
from bot.models.lock import Lock


class Locks:
    """
    В каждом блокировщике есть queue и message.
    Атрибут queue заполнять и определять - не нужно!
    В message - указываем текст сообщения, которое будет выдаваться при блокировке.

    :cvar classic: Классический блокировщик без привязки к определенному функционалу.
    """

    classic = Lock(message="В этом чате уже кто-то использует эту команду. Попробуйте через несколько секунд.")
