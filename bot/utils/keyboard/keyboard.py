from bot.utils.keyboard.button import button, ButtonType
from bot.utils.keyboard.colors import Colors


class Keyboard:
    example = (
        button(
            visible_text="Видимый текст",
            text="Вводимый текст",
            color=Colors.green,
            button_type=ButtonType.CALLBACK,
        ),
        button(text="line"),
        button(
            visible_text="Видимый текст",
            text="Вводимый текст",
            color=Colors.blue,
            button_type=ButtonType.TEXT,  # По умолчанию
        ),
    )
