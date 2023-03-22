from abc import ABC
import asyncio
import nest_asyncio
from MainClass import Main
from utils.types import *

nest_asyncio.apply()


# Класс с описаниями всех основных рабочих функций
class MainFunctions(Main, ABC):
    async def example_func_without_params_with_extra(self, event: Event, extra):
        await self.send_message(
            Message(
                event.chat_id,
                "message from user_id: " + str(event.user_id) + "\n" +
                "this is extra_param:" + extra
            )
        )

    async def example_func_with_params(self, event: Event):
        await self.send_message(
            Message(
                event.chat_id,
                "message from user_id: " + str(event.user_id) + "\n" +
                "this is params:" + event.param
            )
        )

    async def example_func_with_attachment(self, event: Event):
        await self.send_message(
            Message(
                event.chat_id,
                "message from user_id: " + str(event.user_id) + "\n" +
                "this is ID of attachment" + str(event.attachment),
                attachment=event.attachment
            )
        )

    async def example_func_only_with_reply(self, event: Event):
        await self.send_message(
            Message(
                event.chat_id,
                "I received a reply from user_id: " + str(event.user_id) + "\n" +
                "Reply: " + str(event.reply_from)
            )
        )

    async def example_callback_func_without_params(self, event: Event):
        await self.callback_message(
            Message(
                event.chat_id,
                "I received a reply from user_id: " + str(event.user_id) + "\n" +
                "CallbackID: " + str(event.callback_id),
                callback_id=event.callback_id
            )
        )

    async def example_callback_func_with_params(self, event: Event):
        await self.callback_message(
            Message(
                event.chat_id,
                "I received a reply from user_id: " + str(event.user_id) + "\n" +
                "CallbackID: " + str(event.callback_id) + "\n" +
                "params: " + event.param,
                callback_id=event.callback_id
            )
        )
