import nest_asyncio

from bot.models.import_all_models import *
from bot.objects.base_module import BaseModule

nest_asyncio.apply()


class ExampleFuncs(BaseModule):
    """
    Example class с примерами разных типов функций и работы с ними
    """

    async def example_func_without_params_with_extra(self, event: Event, extra) -> Message:
        """
        Пример функции без параметров с дополнительным экстра

        :param event: Platform Event obj.
        :param extra: Extra Param
        :return: Message obj.
        """

        return Message(
            event.chat_id,
            await self.bot.bold("message from user_id: ") + str(event.user_id) + "\n" +
            await self.bot.bold("this is extra_param: ") + extra
        )

    async def example_func_with_params(self, event: Event) -> Message:
        """
        Пример функции с параметром без экстра.

        :param event: Platform Event obj.
        :return: Message obj.
        """
        return Message(
            event.chat_id,
            await self.bot.bold("message from user_id: ") + str(event.user_id) + "\n" +
            await self.bot.bold("this is params: ") + event.param
        )

    async def example_func_with_attachment(self, event: Event) -> Message:
        """
        Пример функции с вложенным ImageID.

        :param event: Platform Event obj.
        :return: Message obj.
        """
        return Message(
            event.chat_id,
            await self.bot.bold("message from user_id: ") + str(event.user_id) + "\n" +
            await self.bot.bold("this is ID of attachment: ") + str(event.attachment),
            attachment=event.attachment
        )


    async def example_func_only_with_reply(self, event: Event) -> Message:
        """
        Пример функции с reply.

        :param event: Platform Event obj.
        :return: Message obj.
        """
        return Message(
            event.chat_id,
            await self.bot.bold("I received a reply from user_id: ") + str(event.user_id) + "\n" +
            await self.bot.bold("Reply: ") + str(event.reply_from)
        )

    async def example_callback_func_without_params(self, event: Event):
        """
        Пример функции Callback.

        :param event: Platform Event obj.
        """
        message = Message(
            event.chat_id,
            await self.bot.bold("I received a reply from user_id: ") + str(event.user_id) + "\n" +
            await self.bot.bold("CallbackID: ") + str(event.callback_id),
            callback_id=event.callback_id
        )

        await self.bot.callback_message(
            message=message,
            alert=True
        )

    async def example_callback_func_with_params(self, event: Event):
        """
        Пример функции Callback с параметрами.

        :param event: Platform Event obj.
        """
        message = Message(
            event.chat_id,
            await self.bot.bold("I received a reply from user_id: ") + str(event.user_id) + "\n" +
            await self.bot.bold("CallbackID: ") + str(event.callback_id) + "\n" +
            await self.bot.bold("params: ") + event.param,
            callback_id=event.callback_id
        )

        await self.bot.callback_message(
            message,
            alert=True
        )
