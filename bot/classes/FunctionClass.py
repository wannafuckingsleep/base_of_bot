from abc import ABC
import nest_asyncio
from bot.classes.MainClass import Main

from bot.models.import_all_models import *

nest_asyncio.apply()


# Класс с описаниями всех основных рабочих функций
class MainFunctions(Main, ABC):
    async def example_func_without_params_with_extra(self, event: Event, extra):
        await self.send_message(
            Message(
                event.chat_id,
                await self.bold("message from user_id: ") + str(event.user_id) + "\n" +
                await self.bold("this is extra_param: ") + extra
            )
        )

    async def example_func_with_params(self, event: Event):
        await self.send_message(
            Message(
                event.chat_id,
                await self.bold("message from user_id: ") + str(event.user_id) + "\n" +
                await self.bold("this is params: ") + event.param
            )
        )

    async def example_func_with_attachment(self, event: Event):
        await self.send_message(
            Message(
                event.chat_id,
                await self.bold("message from user_id: ") + str(event.user_id) + "\n" +
                await self.bold("this is ID of attachment: ") + str(event.attachment),
                attachment=event.attachment
            )
        )

    async def example_func_only_with_reply(self, event: Event):
        await self.send_message(
            Message(
                event.chat_id,
                await self.bold("I received a reply from user_id: ") + str(event.user_id) + "\n" +
                await self.bold("Reply: ") + str(event.reply_from)
            )
        )

    async def example_callback_func_without_params(self, event: Event):
        await self.callback_message(
            Message(
                event.chat_id,
                await self.bold("I received a reply from user_id: ") + str(event.user_id) + "\n" +
                await self.bold("CallbackID: ") + str(event.callback_id),
                callback_id=event.callback_id
            )
        )

    async def example_callback_func_with_params(self, event: Event):
        await self.callback_message(
            Message(
                event.chat_id,
                await self.bold("I received a reply from user_id: ") + str(event.user_id) + "\n" +
                await self.bold("CallbackID: ") + str(event.callback_id) + "\n" +
                await self.bold("params: ") + event.param,
                callback_id=event.callback_id
            )
        )

    @staticmethod
    async def is_int(s):  # Проверка целочисленности
        try:
            s = int(s)
            return s
        except:
            return False
