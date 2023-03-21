import asyncio
import nest_asyncio
from utils.types import Keyboard

nest_asyncio.apply()


class Main:

    # Лок, который блокирует одновременное выполнение одинаковых команд в одном чате.
    # Используется в CommandClass.py
    command_lock: dict = {
        "queue": {},
        "message": "Попробуйте использовать команду через 5 секунд"  # Текст, который будет выдавать лок
    }

    def __init__(self):
        pass
