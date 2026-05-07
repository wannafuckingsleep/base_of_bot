import asyncio
import traceback
from typing import Optional

from vkbottle import Keyboard, Text, VKAPIError, KeyboardButtonColor, Callback
from vkbottle.bot import Bot
import re

from bot.classes.commands import Commands
from bot.objects.emojies import set_platform
from settings import product_server, platform_tokens
from re import findall
from bot.models.message import Message
from loguru import logger

from bot.utils.images import Images


class VkClass(Commands):
    platform = 'vk'
    base = ('base_of_bot', 'base_of_bot')  # Название БД. Вторая база - для тестового бота

    bot_id = (1124824021, 1137923067)  # Первый - основной бот, второй - тестовый
    vk_color = {  # Цвета клавиатур вк
        'blue': KeyboardButtonColor.PRIMARY,  # Синяя
        'white': KeyboardButtonColor.SECONDARY,  # Белая
        'red': KeyboardButtonColor.NEGATIVE,  # Красная
        'green': KeyboardButtonColor.POSITIVE,  # Зелёная
    }
    admins = (569930838,)  # ID админов
    image = Images(platform)

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

    def __init__(self):
        set_platform(self.platform)
        self.distribute_commands()
        self.distribute_platform_commands()
        logger.remove()
        product_index = 0 if product_server else 1
        self.base = self.base[product_index]
        self.group_id = self.bot_id[product_index]
        self.bot = Bot(platform_tokens['vk'])
        self.bot.labeler.message_view.replace_mention = True

        super().__init__()  # Вызов конструктора класса родителя

        # Добавляем в список команд, специфичные для платформы команды

    def start_receiving_updates(self):  # Старт получения апдейтов
        self.bot.loop_wrapper.add_task(self.on_startup())
        self.bot.run_forever()

    async def generate_keyboard(self, buttons):  # Генерация клавиатуры
        if buttons is None or len(buttons) == 0:
            return None

        keyboard = Keyboard(inline=True)  # Инициируем клавиатуру
        for button in buttons:  # Обрабатываем все кнопки
            # Пропускаем переводы строк, которые для других соц. сетей
            if button['text'] == 'tg_line':
                continue

            # Добавляем перевод на новую строку
            if button['text'] in ('line', 'vk_line'):
                keyboard.row()
                continue

            if 'type' in button and button['type'] in ('callback', 'vk_callback'):
                keyboard.add(
                    Callback(
                        label=button['visible_text'],
                        payload={'cmd': button['text']}
                    )
                )
                continue

            if 'type' in button and button['type'] == 'tg_callback':
                keyboard.add(
                    Text(label=button['visible_text']),
                    color=self.vk_color[button['color']]
                )
                continue

            keyboard.add(
                Text(label=button['text']),
                color=self.vk_color[button['color']]
            )

        keyboard = keyboard.get_json()  # Генерируем объект клавиатуры
        return keyboard

    async def get_message_id(self, message):  # Получение ID отправленного сообщения
        if (
            message and
            len(message) > 0 and
            hasattr(message[0], 'conversation_message_id')
        ):
            return message[0].conversation_message_id

        return None

    # Форвардим сообщение
    async def forward_message(self, to_chat, from_chat, message_id, need_exception=False):
        pass

    async def send_message(self, message: Message, send_long_message=True):
        try:

            message.ping = not message.ping

            forward = None
            if message.reply_to_message_id:
                forward = {
                    "conversation_message_ids": [message.reply_to_message_id],
                    "peer_id": message.chat_id,
                    "is_reply": True
                }

            msg = await self.bot.api.messages.send(
                peer_ids=[message.chat_id],
                message=message.message,
                attachment=message.attachment,
                disable_mentions=message.ping,
                keyboard=message.keyboard,
                random_id=0,
                dont_parse_links=not message.web_page_preview,
                forward=forward
            )

            if msg[0].error:
                return await self.write_msg_errors(msg[0].error.code)

            return msg

        except VKAPIError[914]:
            if send_long_message:
                pass

        except (VKAPIError[6], VKAPIError[9]) as e:
            async def recursive_call(exception):
                if hasattr(exception, 'timeout'):
                    timeout = exception.timeout

                else:
                    timeout = 1

                await asyncio.sleep(timeout)
                await self.send_message(message)  # Recursive call

            task = asyncio.create_task(recursive_call(e))

        except Exception as err:

            if not product_server:
                print(traceback.format_exc())

            if message.need_log:
                await self.write_log(
                    'send_message_log',
                    f"{message.__dict__}\n" + traceback.format_exc()
                )

            if message.need_exception:
                return await self.write_msg_errors(err)

    # Удаляем сообщение
    async def delete_message(self, message: Message):
        try:
            await self.bot.api.messages.delete(
                conversation_message_ids = message.message_id,
                peer_id = message.chat_id,
                delete_for_all = True
            )

        except:
            if not product_server:
                print(message.chat_id, message.message_id, traceback.format_exc())

    async def edit_message(self, message: Message):
        try:

            await self.bot.api.messages.edit(
                peer_id=message.chat_id,
                message=message.message,
                conversation_message_id=message.message_id,
                attachment=message.attachment,
                keyboard=message.keyboard
            )

        except (VKAPIError[6], VKAPIError[9]) as e:
            async def recursive_call(exception):
                timeout = 1
                if hasattr(exception, 'timeout'):
                    timeout = exception.timeout

                await asyncio.sleep(timeout)
                await self.edit_message(message)  # Recursive call

            task = asyncio.create_task(recursive_call(e))

        except VKAPIError[914]:
            return "TooLongMessage"

        except Exception:
            await self.write_log(
                'send_message_log',
                f"{message.chat_id}\n{message.message}\n{message.attachment}\n" + traceback.format_exc()
            )

    # Получение юзера человека, с которым нужно будет взаимодействовать
    async def get_destination(self, param, reply_from):
        if reply_from is not None:
            return reply_from

        elif param is None:
            return None

        param = findall(r"\[id(\d*)\|", param)
        if (
            not param or
            not await self.is_int(param[0])
        ):
            return None

        destination = int(param[0])
        if destination > 0:
            return destination

        return None


    async def is_admin(self, user_id, chat_id):  # Является ли пользователь админом
        try:

            members = await self.bot.api.messages.get_conversation_members(
                peer_id=chat_id,
                fields=['is_admin']
            )
            for i in members.items:
                if i.member_id != user_id:
                    continue

                if i.is_admin:
                    return True

                return False

        except:
            message = '🤕' + 'Для нормальной работы, нужно выдать мне админ-права' + '🤕'
            await self.send_message(
                Message(
                    chat_id,
                    message,
                )
            )
            return True

    # Получение имени пользователя с возможностью упомянуть его
    async def get_name(
            self, user_id: int,
            chat_id: int,
            ping: bool = False,
            special_name: Optional[str] = None
    ) -> str:
        # Если не нужно упоминание, но задаётся имя, то надо просто вернуть имя
        if not ping and special_name is not None:
            return special_name

        user_info, = await self.bot.api.users.get(user_id=user_id, random_id=0)
        user_name = user_info.first_name + " " + user_info.last_name

        if ping:  # Если нужно упоминание
            if special_name is None:
                user_name = special_name

            return f'[id{user_id}|{user_name}]'

        return user_name

    async def get_attachment_id(self, event, need_all=False):  # Получаем id вложения
        pass

    async def escape_string(self, s) -> Optional[str]:  # Экранирование строки
        return re.sub(f'\\[.+?\\|.+?]', '', s)

    async def make_link(self, title, link):  # Формируем ссылку
        try:
            link = int(link)
            link = f'id{link}'
        except:
            pass

        return f'[{link}|{title}]'

    @staticmethod
    async def link_to_user(user_id):  # Получаем ссылку на пользователя
        return str(user_id)

    @staticmethod
    async def bold(s):  # Делаем текст жирным
        return s

    @staticmethod
    async def italic(s):  # Делаем текст курсивом
        return s

    @staticmethod
    async def underline(s):  # Делаем текст подчеркнутым
        return s

    @staticmethod
    async def code(s):  # Делаем текст monospace
        return s

    async def callback_message(self, message: Message, alert=True):
        event_data = {
            "type": "show_snackbar",
            "text": message.message
        }

        await self.bot.api.messages.send_message_event_answer(
            message.callback_id,
            user_id=message.user_id,
            peer_id=message.chat_id,
            event_data=str(event_data)
        )

    async def is_chat(self, chat_id):
        if chat_id > 2000000000:
            return True

        return False
