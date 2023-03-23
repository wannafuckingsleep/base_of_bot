import re
import traceback
from typing import Union

from vkbottle import GroupEventType
from vkbottle_types import GroupTypes
from vkbottle.bot import Message
from bot.utils.types import Event

from bot.classes.VkClass import VkClass

need_debug_log = False
if need_debug_log:  # Log for debug to console and/or file
    import logging

    # file_log = logging.FileHandler('vk_debug.txt') #Если нужно логирование в файл надо этот handler добавить
    # в handlers рядом с консольным
    console_out = logging.StreamHandler()
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=(console_out,), )
else:
    from loguru import logger

    logger.remove()
print('start')

toadbot = VkClass()
toadbot.bot.labeler.message_view.replace_mention = True


# Ловим лайки на пост
@toadbot.bot.on.raw_event(GroupEventType.LIKE_ADD, dataclass=GroupTypes.LikeAdd)
async def main_menu(event: GroupTypes.LikeAdd):
    try:
        if event.object.object_type.value == 'post':
            user = event.object.liker_id
            wall_id = event.object.object_id
    except:
        await VkClass.write_log('vk_add_like', f'{str(event)}\n{traceback.format_exc()}')


# Ловим дизлайки на пост
@toadbot.bot.on.raw_event(GroupEventType.LIKE_REMOVE, dataclass=GroupTypes.LikeRemove)
async def main_menu(event: GroupTypes.LikeRemove):
    try:
        if event.object.object_type.value == 'post':
            user = event.object.liker_id
            wall_id = event.object.object_id
    except:
        await VkClass.write_log('vk_remove_like', f'{str(event)}\n{traceback.format_exc()}')


@toadbot.bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=GroupTypes.MessageEvent)
async def main_menu(platform_event: GroupTypes.MessageEvent):
    try:
        platform_event = platform_event.object
        message = platform_event.payload.get('cmd')
        message = message.lower()
        message = message.replace('ё', 'е')
        extra: [dict, None] = None
        event: Union[Event, None] = None
        for command_type, command_list in toadbot.bot_commands.items():
            if command_type.find('callback') == -1:
                continue  # Если это не callback команда, то обрабатываем не тут
            if command_type.find('_with_params') == -1:
                with_params = False
            else:
                with_params = True
            clean_event_text = platform_event.payload.get('cmd')

            if with_params:
                event, extra = await toadbot.check_event_in_commands(message, command_list,
                                                                     with_params=True,
                                                                     clean_event_text=clean_event_text)
            else:
                event, extra = await toadbot.check_event_in_commands(message, command_list)
            if event:
                event.user_id = platform_event.user_id
                event.peer_id = platform_event.peer_id
                event.message_id = platform_event.conversation_message_id
                event.callback_id = platform_event.event_id
                break
        if event:
            await toadbot.execute_command(event, extra, 'VK_CALLBACK_MESSAGES')

    except:
        await VkClass.write_log('vk_callback', f'{str(platform_event)}\n{traceback.format_exc()}')


@toadbot.bot.on.message()
async def echo(platform_event: Message):
    try:
        peer_id = platform_event.peer_id
        user = platform_event.from_id

        if user > 0:  # Убрать это условие, если бот должен реагировать на других ботов
            # Если бота добавили в чат
            if (platform_event.action and str(
                    platform_event.action.type
            ) == 'MessagesMessageActionStatus.CHAT_INVITE_USER'
                    and platform_event.action.member_id == -toadbot.group_id):
                pass

            attachment = platform_event.attachments
            message = platform_event.text.lower()

            if hasattr(platform_event.mention, 'id') and abs(platform_event.mention.id) not in toadbot.bot_id:
                message += str(platform_event.mention.id)
            message = re.sub(f'\\[.+?\\|.+?] ', '', message)  # удаление тега бота первым словом
            message = message.replace('ё', 'е')
            message = message.strip()
            clean_event_text = platform_event.text
            if hasattr(platform_event.mention, 'id') and abs(platform_event.mention.id) not in toadbot.bot_id:
                clean_event_text += str(platform_event.mention.id)
            # Добавить сюда слова с буквой ё для их замены на е
            # clean_event_text = re.sub('ёлка', 'елка', clean_event_text, flags=re.I)
            clean_event_text = re.sub(f'\\[.+?\\|.+?] ', '', clean_event_text)
            clean_event_text = clean_event_text.strip()
            if platform_event.reply_message:
                reply_from = platform_event.reply_message.from_id
            else:
                reply_from = None

            extra: [dict, None] = None
            event: Union[Event, bool] = False

            for command_type, command_list in toadbot.bot_commands.items():  # Проходим по всем спискам команд бота
                need_check = False
                if command_type.find('callback') != -1:
                    continue  # Если это callback команда, то обрабатываем не тут
                if command_type.find('_with_params') == -1:
                    with_params = False
                else:
                    with_params = True
                if command_type.find('_with_attachment') == -1:
                    with_attachment = False
                else:
                    with_attachment = True

                if with_attachment and len(platform_event.attachments) > 0:
                    need_check = True
                elif reply_from is None and command_type.find('_with_reply') != -1:
                    need_check = False
                elif len(platform_event.attachments) == 0 and not with_attachment:
                    need_check = True

                if need_check:
                    if with_params:
                        event, extra = await toadbot.check_event_in_commands(message, command_list,
                                                                             with_params=True,
                                                                             clean_event_text=clean_event_text)
                    else:
                        event, extra = await toadbot.check_event_in_commands(message, command_list)
                if event:
                    event.user_id = user
                    event.peer_id = peer_id
                    event.username = f"id{user}"
                    event.attachment = attachment
                    event.message_id = platform_event.conversation_message_id
                    event.destination = await toadbot.get_destination(event.param, reply_from)
                    if user < 0:
                        event.is_bot = True
                    break
            if event:
                await toadbot.execute_command(event, extra, 'VK_TEXT_MESSAGES')

            if platform_event.from_id in toadbot.admins:  # commands for admins
                if message == 'reboot':
                    await toadbot.mysql_connect()
                    await toadbot.reboot(platform_event.from_id)
    except:
        await VkClass.write_log('vk_log', f'{str(platform_event)}\n{traceback.format_exc()}')


toadbot.start_receiving_updates()
