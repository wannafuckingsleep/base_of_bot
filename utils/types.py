from typing import Union, Optional


class Colors:
    blue = "blue"
    green = "green"
    red = "red"
    white = "white"


def button(
         text: str = None,
         visible_text: Union[str, bool] = None,
         callback: bool = False,
         color: str = Colors.blue,
) -> dict:

    """
    Если нужна новая строка, вызывается без параметров
    :param text: Задается текст
    :param visible_text: Видимый текст
    :param callback: True if callback
    :param color: use Colors.*red*
    :return: словарь для генерации в клавиатуру для платформы
    """

    # if new_line:
    #     return {"text": "line"}
    if not any((text, visible_text)):
        return {"text": "line"}
    if visible_text is None:
        visible_text = text

    current_button = {
        "text": text,
        "visible_text": visible_text,
        "color": color
    }
    if callback:
        current_button['type'] = "callback"
    return current_button


class Keyboard:
    example = (
        button(
            visible_text="Видимый текст",
            text="Вводимый текст",
            color=Colors.green,
            callback=False
        ),
        button(text="line"),
        button(
            visible_text="Видимый текст",
            text="Вводимый текст",
            color=Colors.blue,
            callback=True
        ),
    )