# Телеграм бот
import asyncio
import json
import re
import traceback
from datetime import datetime
from typing import Union

from aiogram import types
from aiogram.types import ContentTypes, Message
from bot.utils.types import Event, Message as ToadbotMessage

from bot_settings import platform_tokens
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


@bot.dp.callback_query_handler()
async def callback_menu(query: types.CallbackQuery):
    try:
        start_time = datetime.now()
        message = query.data.lower()
        chat_id = query.message.chat.id
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
                event, extra = await bot.check_event_in_commands(
                    message, command_list, with_params=True,
                    clean_event_text=clean_event_text)
            else:
                event, extra = await bot.check_event_in_commands(message, command_list)

            if event:
                event.user_id = user
                event.chat_id = chat_id
                event.username = query.from_user.username
                event.message_id = query.message.message_id
                event.callback_id = query.id
                break

        await bot.execute_command(event, extra, 'TG_CALLBACK_MESSAGES')

        if need_debug_log:
            log_str = str(datetime.now() - start_time) + ' ||| ' + str(query)
            await bot.write_log('tg_callback_command_log', log_str)
    except:
        await bot.write_log('tg_callback', f'{str(query)}\n{traceback.format_exc()}')


@bot.dp.message_handler(content_types=
                        ContentTypes.TEXT & ContentTypes.ANIMATION & ContentTypes.PHOTO &
                        ContentTypes.NEW_CHAT_MEMBERS & ContentTypes.MIGRATE_TO_CHAT_ID &
                        ContentTypes.MIGRATE_FROM_CHAT_ID)
async def text_menu(platform_event: Message):
    try:
        start_time = datetime.now()

        chat_id = platform_event.chat.id
        user = platform_event.from_user.id

        if getattr(platform_event, 'migrate_from_chat_id'):  # отлов смены ID Чата
            try:
                next_peer = platform_event.sender_chat.id
                last_peer = platform_event.migrate_from_chat_id
                await bot.chat_migrate(last_peer, next_peer)
            except:
                await bot.write_log('migrate', f'{str(platform_event)}\n{traceback.format_exc()}')

        # Проверка на добавление нового пользователя
        if platform_event.new_chat_members:  # Добавление бота
            member = platform_event.new_chat_members[0]['id']
            if member in bot.bot_id:
                pass

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
                elif platform_event.document is not None and platform_event.document.mime_type in (
                        'video/mp4', 'image/gif'):
                    attachment = platform_event.document.file_id
                    message_type = 'gif'
                    need_check = True
            elif platform_event.text is not None and command_type != 'message_commands_with_attachment':

                # Если это не форвард
                if not getattr(platform_event, 'forward_from') and not getattr(platform_event, "forward_sender_name"):
                    need_check = True
                    username = platform_event.from_user.username
                    # заменить на проверку username бота из bot_info
                    platform_event.text = re.sub('(@toadbot |@toadbot|@testtoadbot |@testtoadbot)', '',
                                                 platform_event.text,
                                                 flags=re.I)
                    message = platform_event.text.lower()
                    clean_event_text = platform_event.text
                    # Замена буквы ё
                    # clean_event_text = re.sub('жабёнку', 'жабенку', clean_event_text, flags=re.I)

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
                if user == 1087968824:  # Установка анонимного аккаунта как бот-аккаунт
                    event.is_bot = True

                event.destination = await bot.get_destination(event.param, reply_from)

                if platform_event.chat.is_forum is None:
                    event.is_forum = False
                else:
                    event.is_forum = platform_event.chat.is_forum
                    if platform_event.reply_to_message and \
                            platform_event.reply_to_message.is_topic_message:
                        event.thread_id = platform_event.message_thread_id
                    else:
                        event.is_forum = False
                break
        if event:
            await bot.execute_command(event, extra, 'TG_TEXT_MESSAGES')

        # ______________________________________________________________________ #

        if user in bot.admins:  # блок команд для админов
            if platform_event.text == 'reboot':
                await bot.reboot(user)
            elif platform_event.text == 'get id':
                file_id = await bot.get_attachment_id(platform_event, need_all=True)
                await bot.send_message(
                    ToadbotMessage(chat_id, file_id)
                )

            elif platform_event.text == 'webhook info' and platform_event.chat.type == 'private':
                url = f"https://api.telegram.org/bot{platform_tokens['tg']}/getWebhookInfo"
                webhook_info = await bot.download_file(url)
                if webhook_info:
                    webhook_info = json.loads(webhook_info)
                    if 'result' in webhook_info:
                        if 'url' in webhook_info['result']:
                            del webhook_info['result']['url']
                        if 'ip_address' in webhook_info['result']:
                            del webhook_info['result']['ip_address']
                        if 'last_error_date' in webhook_info['result']:
                            webhook_info['result']['last_error_date'] = datetime.utcfromtimestamp(
                                int(webhook_info['result']['last_error_date'])).strftime('%Y-%m-%d %H:%M:%S')
                        webhook_info['asyncio tasks'] = len(asyncio.all_tasks())
                    webhook_info = json.dumps(webhook_info, indent=4)
                    await bot.send_message(ToadbotMessage(platform_event.chat.id, webhook_info))
        if need_command_log:
            log_str = str(datetime.now() - start_time) + ' ||| ' + str(event)
            await bot.write_log('tg_command_log', log_str)
    except:
        print(traceback.format_exc())


bot.start_receiving_updates()
