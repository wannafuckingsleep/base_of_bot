"""
Объявляем базовый класс, от которого будут наследоваться все функциональные модули.
"""
# from bot.classes.MainClass import Main
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.classes.MainClass import Main  # Импорт только для проверки типов

class BaseModule:
    """
    Базовый класс для всех функциональных модулей.

    :param bot: Объект класса MainBot.
    :cvar bot: Объект класса MainBot.
    """
    bot: "Main"

    def __init__(self, bot: "Main"):
        self.bot = bot