#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os

from config import Config
# the Strings used for this "thing"
from translation import Translation

from pyrogram import filters
from database.adduser import AddUser
from pyrogram import Client as Clinton
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from . import mediafire
from . import dl_button

@Clinton.on_message(filters.command(["mediafire"]))
async def dl_mediafire(bot, update):
    # logger.info(update)
    # await AddUser(bot, update)
    # test 👇
    url = update.text.split()[1]
    r = mediafire.get(url)
    dl_link, filename = r.split("|")
    print(filename)
    print(dl_link)
    video_formats = ["mp4", "mkv", "webm"]
    dl_ext = filename.split(".")[-1]
    if dl_ext in video_formats:
      send_type = "video"
    else:
      send_type = "file"
    update.data = "{}={}={}".format(send_type, 0, dl_ext)
    await dl_button.ddl_call_back(bot, update, dl_link)
    """
    await bot.send_message(
        chat_id=update.chat.id,
        text=dl_link,
        parse_mode="html",
        disable_web_page_preview=True,
        reply_to_message_id=update.message_id
    )
    """

@Clinton.on_message(filters.reply & filters.text)
async def edit_caption(bot, update):
    #logger.info(update)
    try:
        await bot.send_cached_media(
            chat_id=update.chat.id,
            file_id=update.reply_to_message.video.file_id,
            reply_to_message_id=update.message_id,
            caption=update.text
        )
    except:
        await bot.send_cached_media(
            chat_id=update.chat.id,
            file_id=update.reply_to_message.document.file_id,
            reply_to_message_id=update.message_id,
            caption=update.text
        )
        
@Clinton.on_message(filters.private & filters.command(["help"]))
async def help_user(bot, update):
    # logger.info(update)
    await AddUser(bot, update)
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.HELP_USER,
        parse_mode="html",
        disable_web_page_preview=True,
        reply_to_message_id=update.message_id
    )

@Clinton.on_message(filters.private & filters.command(["addcaption"]))
async def add_caption_help(bot, update):
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.ADD_CAPTION_HELP,
        parse_mode="html",
        reply_to_message_id=update.message_id
    )

@Clinton.on_message(filters.private & filters.command(["start"]))
async def start(bot, update):
    # logger.info(update)
    await AddUser(bot, update)
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.START_TEXT.format(update.from_user.mention),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Source code ⚡", url="https://github.com/wywxz/SimpleUploaderBot"
                    ),
                    InlineKeyboardButton("Developer 👨‍⚖️", url="https://t.me/SimpleBotsChannel"),
                ],
            ]
        ),
        reply_to_message_id=update.message_id
    )
