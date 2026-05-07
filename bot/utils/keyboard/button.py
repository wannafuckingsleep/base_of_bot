from dataclasses import dataclass
from bot.utils.keyboard.colors import Colors


@dataclass
class BaseButton:
    """
    Базовый класс для кнопок.
    """
    visible_text: str = None
    color: str = Colors.blue


@dataclass
class CallbackButton(BaseButton):
    """
    Базовый класс для колбэк кнопок.
    """
    text: str = None

    def __post_init__(self):
        if self.visible_text is None:
            self.visible_text = self.text


@dataclass
class CallbackButtonTG(CallbackButton):
    """
    Класс для TG колбэк кнопок.
    """


@dataclass
class CallbackButtonVK(CallbackButton):
    """
    Класс для VK колбэк кнопок.
    """


@dataclass
class InlineButton(BaseButton):
    """
    Класс для текстовых кнопок.
    """
    text: str = None

    def __post_init__(self):
        if self.visible_text is None:
            self.visible_text = self.text


@dataclass
class AddBotButton(BaseButton):
    """
    Класс для кнопок добавить бота.
    """


@dataclass
class LinkButton(BaseButton):
    """
    Класс для кнопок со ссылками.
    """
    link: str = None


@dataclass
class EmptyLine(BaseButton):
    """
    Кнопка с пустой строкой.
    """


@dataclass
class EmptyLineTG(BaseButton):
    """
    Кнопка с пустой строкой только в ТГ.
    """


@dataclass
class EmptyLineVK(BaseButton):
    """
    Кнопка с пустой строкой только в ВК.
    """
