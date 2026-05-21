from bot.objects.links.max_links import MaxLinks
from bot.objects.links.tg_links import TgLinks
from bot.objects.links.vk_links import VkLinks


class Links:
    """
    Объект ссылок.

    :cvar example_link: Пример ссылки.
    """
    example_link: str

    def __init__(self, platform):
        if platform == "tg":
            platform_object = TgLinks

        elif platform == "vk":
            platform_object = VkLinks

        else:  # platform == "max"
            platform_object = MaxLinks

        self.example_link = platform_object.example_link
