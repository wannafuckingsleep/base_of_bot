import typing
from typing import Union, Optional
from enum import Enum
from bot.utils.keyboard.colors import Colors


class ButtonType(str, Enum):
    """
    :cvar CALLBACK: Кнопка с вызовом callback.
    :cvar TEXT: Кнопка с текстом.
    :cvar ADD_BOT: Кнопка добавления бота.
    :cvar LINK: Кнопка со ссылкой.
    """
    CALLBACK = "callback"
    TEXT = "text"
    ADD_BOT = "add_bot"
    LINK = "link"

    VK_CALLBACK = "vk_callback"
    TG_CALLBACK = "tg_callback"


def button(
        text: str = None,
        visible_text: Union[str, bool] = None,
        color: str = Colors.blue,
        button_type: ButtonType = ButtonType.TEXT,
        link: Optional[str] = None
) -> dict:

    """
    Кнопка для генерации клавиатуры.
    Если нужна новая строка, вызывается без параметров.

    :param text: Задается текст
    :param visible_text: Видимый текст
    :param color: use Colors.*red*
    :param button_type: тип кнопки. Object of ButtonType.
    :param link: Ссылка, если ButtonType=LINK.

    :return: Словарь для генерации в клавиатуру для платформы
    """
    if not any((text, visible_text)):
        return {"text": "line"}

    if visible_text is None:
        visible_text = text

    current_button = {
        "text": text,
        "visible_text": visible_text,
        "color": color,
        "type": button_type,
        "link": link
    }

    return current_button
