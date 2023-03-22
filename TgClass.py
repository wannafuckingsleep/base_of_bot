# example of platform class based on TG
import asyncio
import random
import traceback
from typing import Union, Optional, Literal

from aiogram import Bot, Dispatcher, executor, types, md
from aiogram.utils import exceptions, deep_linking

from CommandClass import Commands
from settings import platform_tokens, product_server
from utils.types import Event, Message


class TgClass(Commands):

    platform = "tg"
    base = ('base_of_bot', 'test_base_of_bot')  # Название БД. Вторая база - для тестового бота

    webhook_host = ""  # При необходимости, добавить вебхук
    webhook_path = f'/{platform_tokens["tg"]}'
    webhook_url = f'{webhook_host}{webhook_path}'

    webhook_port = (5001, 5000)  # 5000 - для тестового бота, 5001 - для основного бота

    admins = (177237242, )  # ID админов

    def __init__(self):
        super().__init__()  # Вызов конструктора класса родителя
        product_index = 0 if product_server else 1
        self.webhook_port = self.webhook_port[product_index]

        self.bot = Bot(platform_tokens['tg'], parse_mode=types.ParseMode.HTML)
        self.dp = Dispatcher(self.bot, run_tasks_by_default=True)
        self.distribute_commands()
        self.distribute_platform_commands()

    # Команды, которые нужно добавить специально для этой платформы
    def distribute_platform_commands(self, ):
        specific_bot_commands = {  # Специфичные для платформы команды
            'message_commands': (),
            'message_commands_with_params': (),
            'message_commands_with_reply': (),
            'message_commands_with_attachment': (),
            'callback_messages': (),
            'callback_messages_with_params': (),
        }
        for command_type in self.bot_commands.keys():
            self.bot_commands[command_type] = self.bot_commands[command_type] + specific_bot_commands[command_type]

    def start_receiving_updates(self):  # Старт получения апдейтов
        async def on_startup(dp):  # Общая функция, срабатывающая при запуске получения апдейтов
            if product_server:
                await on_startup_webhook(dp)
            await self.on_startup()

        async def on_startup_webhook(dp):  # Общая функция, срабатывающая при запуске вебхука
            allowed_updates = ["message", "callback_query"]
            await self.bot.set_webhook(self.webhook_url, max_connections=100, allowed_updates=allowed_updates)

        async def on_shutdown(dp):
            # Remove webhook (not acceptable in some cases)
            await self.bot.delete_webhook()

            # Close DB connection (if used)
            await dp.storage.close()
            await dp.storage.wait_closed()
            await self.on_shutdown()

        if product_server:
            print('start webhook')
            executor.start_webhook(
                dispatcher=self.dp,
                webhook_path=self.webhook_path,
                on_startup=on_startup,
                on_shutdown=on_shutdown,
                host='localhost',
                port=self.webhook_port,
                skip_updates=True,
            )
        else:
            print('start polling')
            executor.start_polling(self.dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)

    async def generate_keyboard(self, buttons):  # Генерация клавиатуры
        if buttons is None or len(buttons) == 0:
            return None
        # Инициируем клавиатуру
        keyboard = types.InlineKeyboardMarkup()
        for button in buttons:  # Обрабатываем все кнопки
            if button['text'] in ('line', 'tg_line'):
                keyboard.row()
            elif button['text'] == 'vk_line':
                continue
            else:
                if 'type' in button and button['type'] in ('callback', 'tg_callback'):
                    keyboard.insert(types.InlineKeyboardButton(
                        text=button['visible_text'], callback_data=button['text']))
                else:
                    keyboard.insert(types.InlineKeyboardButton(
                        text=button['visible_text'], switch_inline_query_current_chat=button['text']))
        return keyboard

    async def send_message(self, message: Message, send_long_message=True):
        if message is not None:
            if message.chat is None:
                message.chat = await self.get_chat_settings(message.chat_id)
            try:
                if message.attachment is None:
                    msg = await self.bot.send_message(
                        message.chat_id, message.message, reply_markup=message.keyboard,
                        disable_web_page_preview=True, message_thread_id=message.chat.thread_id
                    )
                else:
                    if message.message_type == 'photo' or message.message_type is None:
                        try:
                            msg = await self.bot.send_photo(
                                message.chat_id, message.attachment, caption=message.message,
                                reply_markup=message.keyboard, message_thread_id=message.chat.thread_id
                            )
                        except:
                            msg = await self.bot.send_animation(
                                message.chat_id, message.attachment, caption=message.message,
                                reply_markup=message.keyboard, message_thread_id=message.chat.thread_id
                            )
                    else:  # message.message_type == 'gif':
                        msg = await self.bot.send_animation(
                            message.chat_id, message.attachment, caption=message.message,
                            reply_markup=message.keyboard, message_thread_id=message.chat.thread_id
                        )
                if message.need_delete and message.chat_id in self.subscribed_chats:  # TODO вынести в общий метод
                    message_id = await self.get_message_id(msg)
                    await self.message_for_delete(message_id=message_id, chat_id=message.chat_id)
                return msg
            except exceptions.RetryAfter as e:
                # Если для всех сообщений делать flood_timeout, то возникает 2 проблемы:
                # 1. Конфликт с текущим механизмом блокировок команд (особенно, если они глобальные, а не по чатам),
                # так как разблокировка происходит только после полного завершения.
                # Есть три варианта решения (можно все использовать одновременно):
                # 1.1. Где не нужна глобальная блокировка - сделать блокировку по чатам. И вообще перегруппировать их.
                # 1.2. (Done) Повторную отправку обернуть в create_task без await'а этого таска (самый хороший вариант)
                # 1.3. Не совсем решение, но определить, для каких сообщений нужен flood_timeout и поставить только
                # для них. Это, как минимум все cron рассылки, результаты сражений, гонок, наград и т.д.
                # 2. У webhook есть лимит в 100 соединений. Если все или большая часть этих соединений остаются висеть,
                # ожидая повторной отправки, то мы не получаем новые события
                async def recursive_call(exception):
                    await asyncio.sleep(exception.timeout)
                    await self.send_message(message)  # Recursive call

                asyncio.create_task(recursive_call(e))
            except exceptions.MigrateToChat as e:
                await self.chat_migrate(message.chat_id, e.migrate_to_chat_id)

                async def recursive_call():
                    message.chat_id = e.migrate_to_chat_id
                    await self.send_message(message)  # Recursive call

                asyncio.create_task(recursive_call())
            except (exceptions.BotKicked, exceptions.Unauthorized, exceptions.ChatNotFound):
                pass
            except exceptions.MessageIsTooLong as e:
                # TODO Сделать отправку слишком длинных сообщений
                pass
            except Exception as err:  # TODO Убрать дублирующийся код (есть ещё в вк), вынести в общий метод
                if not product_server:
                    print(err)
                if message.need_log:
                    await self.write_log('send_message_log',
                                         f"\n{message.__dict__}\n" + traceback.format_exc())
                if message.need_exception:
                    return await self.write_msg_errors(err, message.chat_id)

    # Удаляем сообщение
    async def delete_message(self, message: Message):
        try:
            await self.bot.delete_message(message.chat_id, message.message_id)
        except Exception as e:
            if not product_server:
                # Можно переделать, передавая объект во write_log и формируя строку там
                error_text = ''.join(
                    traceback.format_tb(e.__traceback__)) + e.__class__.__name__ + ': ' + e.__str__()
                print(message.chat_id, message.message_id, error_text)
            pass

    async def edit_message(self, message: Message):
        try:
            if message.message_type == 'caption':
                await self.bot.edit_message_caption(
                    caption=message.message, chat_id=message.chat_id,
                    message_id=message.message_id, reply_markup=message.keyboard)
            else:
                await self.bot.edit_message_text(
                    chat_id=message.chat_id, text=message.message, message_id=message.message_id,
                    reply_markup=message.keyboard)
        except exceptions.RetryAfter as e:
            async def recursive_call(exception):
                await asyncio.sleep(exception.timeout)
                # Recursive call
                await self.edit_message(message)

            asyncio.create_task(recursive_call(e))
        except (exceptions.MessageNotModified, exceptions.MessageToEditNotFound):
            pass
        except exceptions.MessageIsTooLong as e:
            return "TooLongMessage"
        except Exception:
            await self.write_log('send_message_log',
                                 f"{message.chat_id}\n{message.message}\n{message.attachment}\n"
                                 + traceback.format_exc())

    async def callback_message(self, event: Event, alert=True):
        await self.bot.answer_callback_query(
            event.callback_id,
            event.message,
            show_alert=alert
        )

    # Форвардим сообщение
    async def forward_message(self, to_chat, from_chat, message_id, need_exception=False):
        try:
            await self.bot.forward_message(to_chat, from_chat, message_id)
        except Exception as err:
            if not product_server:
                print(err)
            if need_exception:
                return await self.write_msg_errors(err, to_chat)

    @classmethod
    async def get_message_id(cls, message) -> Optional[int]:  # Получение ID отправленного сообщения
        if hasattr(message, 'message_id'):
            return message.message_id
        else:
            return None

    async def is_chat(self, peer_id):
        if peer_id < 0:
            return True
        return False
