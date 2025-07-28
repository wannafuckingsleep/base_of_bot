"""
Модуль, описывающий базовую модель объекта Lock.
"""
from dataclasses import dataclass, field

@dataclass
class Lock:
    """
    Класс описывающий модель lock-объекта. Предназначен для блокировки функций.

    :cvar message: Какое сообщение выведется, если ID чата оказался в queue.
    :cvar queue: Некая очередь ID чатов, в которых запущена эта команда.
    """

    message: str
    queue: dict = field(default_factory=dict)  # создаем пустой словарь для каждого экземпляра по умолчанию
