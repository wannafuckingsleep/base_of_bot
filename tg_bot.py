# Телеграм бот
import asyncio
import json
import re
import traceback
from datetime import datetime
from typing import Union

from aiogram import F
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import deep_linking

from bot.models.platform_event import Event
from settings import platform_tokens
from bot.classes.TgClass import TgClass

need_debug_log = False
if need_debug_log:  # Log for debug to console and/or file :)
    import logging

    # file_log = logging.FileHandler('tg_debug.txt') #Если нужно логирование в файл надо
    # этот handler добавить в handlers рядом с консольным
    console_out = logging.StreamHandler()
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=(console_out,), )

bot = TgClass()

need_command_log = False


# CALLBACK COMMANDS
@bot.dp.callback_query()
async def callback_menu(query: CallbackQuery):
    try:
        message = query.data.lower()
        peer_id = query.message.chat.id
        user = query.from_user.id

        extra: [dict, None] = None
        event: Union[Event, bool] = False

        for command_type, command_list in bot.bot_commands.items():  # Проходим по всем спискам команд бота
            if command_type.find('command') != -1:
                continue

            if command_type.find('_with_params') == -1:
                with_params = False

            else:
                with_params = True

            clean_event_text = query.data
            message = message.replace('ё', 'е')

            if with_params:
                event, extra = await bot.execute_command_logic.check_event_in_commands(
                    message, command_list, with_params=True,
                    clean_event_text=clean_event_text)

            else:
                event, extra = await bot.execute_command_logic.check_event_in_commands(message, command_list)

            if event:
                event.user_id = user
                event.peer_id = peer_id
                event.username = query.from_user.username
                event.message_id = query.message.message_id
                event.callback_id = query.id

                if query.message.chat.is_forum is None:
                    event.is_forum = False

                else:
                    event.is_forum = query.message.chat.is_forum
                    if (
                        query.message.reply_to_message and
                        query.message.reply_to_message.is_topic_message
                    ):
                        event.thread_id = query.message.message_thread_id

                break

        # по идее, всё, что ниже, до except, можно перенести в блок выше до break
        if event:
            await toadbot.execute_command_logic.execute_command(event, extra, 'TG_CALLBACK_MESSAGES')

    except Exception as e:
        await toadbot.write_log('TG_CALLBACK_MESSAGES', f'{str(query)}\n{e}')


# TEXT COMMANDS
@bot.dp.message_handler(
    content_types=ContentTypes.TEXT &
                  ContentTypes.ANIMATION &
                  ContentTypes.PHOTO &
                  ContentTypes.MIGRATE_TO_CHAT_ID &
                  ContentTypes.MIGRATE_FROM_CHAT_ID
)
async def text_menu(platform_event: Message):
    try:
        start_time = datetime.now()

        chat_id = platform_event.chat.id
        user = platform_event.from_user.id

        if getattr(platform_event, 'migrate_from_chat_id'):  # отлов смены ID Чата

            try:
                from_chat = platform_event.sender_chat.id
                to_chat = platform_event.migrate_from_chat_id
                await bot.chat_migrate(from_chat, to_chat)

            except:
                await bot.write_log('migrate', f'{str(platform_event)}\n{traceback.format_exc()}')

        clean_event_text = None
        extra: [dict, None] = None
        event: Union[Event, bool] = False

        # print('bot_commands', toadbot.bot_commands.items())
        for command_type, command_list in bot.bot_commands.items():  # Проходим по всем спискам команд бота
            need_check = False

            if command_type.find('callback') != -1:
                continue  # Если это callback команда, то обрабатываем не тут

            if command_type.find('_with_params') == -1:
                with_params = False

            else:
                with_params = True

            message_type = None
            reply_from = None
            username = None
            attachment = None
            message = None
            message_id = platform_event.message_id

            if command_type == 'message_commands_with_attachment' and platform_event.caption:
                message = platform_event.caption.lower()
                username = platform_event.from_user.username

                if platform_event.photo:
                    attachment = platform_event.photo[-1].file_id
                    message_type = 'photo'
                    need_check = True

                elif (
                        platform_event.document and
                        platform_event.document.mime_type in ('video/mp4', 'image/gif')
                ):
                    attachment = platform_event.document.file_id
                    message_type = 'gif'
                    need_check = True

            elif platform_event.text is not None and command_type != 'message_commands_with_attachment':

                # Если это не форвард
                if not getattr(platform_event, 'forward_from') and not getattr(platform_event, "forward_sender_name"):
                    need_check = True
                    username = platform_event.from_user.username
                    # заменить на проверку username бота из bot_info
                    platform_event.text = re.sub(
                        '(@toadbot |@toadbot|@testtoadbot |@testtoadbot)', '',
                        platform_event.text,
                        flags=re.I
                    )

                    message = platform_event.text.lower()
                    clean_event_text = platform_event.text
                    clean_event_text = re.sub('жабёнку', 'жабенку', clean_event_text, flags=re.I)
                    clean_event_text = re.sub('жабёнка', 'жабенка', clean_event_text, flags=re.I)
                    clean_event_text = re.sub('партнёру', 'партнеру', clean_event_text, flags=re.I)
                    clean_event_text = re.sub('счёт', 'счет', clean_event_text, flags=re.I)

                    if getattr(platform_event, 'reply_to_message'):
                        if platform_event.reply_to_message.forum_topic_created is None:
                            reply_from = platform_event.reply_to_message.from_user.id

                    elif command_type.find('_with_reply') != -1:
                        need_check = False

            if need_check:
                message = message.replace('ё', 'е')
                if with_params:
                    event, extra = await bot.check_event_in_commands(
                        message, command_list, with_params=True,
                        clean_event_text=clean_event_text)

                else:
                    event, extra = await bot.check_event_in_commands(message, command_list)

                if message_type in ('gif', 'photo'):
                    if event:
                        event.param = message_type

            if event:
                event.user_id = user
                event.chat_id = chat_id
                event.username = username
                event.attachment = attachment
                event.message_id = message_id
                event.is_bot = platform_event.from_user.is_bot

                if user in (1087968824, 777000):  # UserID анонимного аккаунта или канала
                    event.is_bot = True

                event.destination = await bot.get_destination(event.param, reply_from)

                if platform_event.chat.is_forum is None:
                    event.is_forum = False

                else:
                    event.is_forum = platform_event.chat.is_forum
                    if (
                            platform_event.reply_to_message and
                            platform_event.reply_to_message.is_topic_message
                    ):
                        event.thread_id = platform_event.message_thread_id
                    else:
                        event.is_forum = False

                break

        if event:
            await bot.execute_command(event, extra, 'TG_TEXT_MESSAGES')

        # ______________________________________________________________________ #

        if user in bot.admins:  # блок команд для админов

            if platform_event.text == 'get id':
                file_id = await bot.get_attachment_id(platform_event, need_all=True)
                await bot.send_message(
                    ToadbotMessage(chat_id, file_id)
                )

        if need_command_log:
            log_str = str(datetime.now() - start_time) + ' ||| ' + str(event)
            await bot.write_log('tg_command_log', log_str)
    except:
        print(traceback.format_exc())


bot.start_receiving_updates()
