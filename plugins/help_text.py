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

import requests
import user_agent

@Clinton.on_message(filters.private & filters.command(["mediafire"]))
async def mediafire_dl(bot, update):
    url = update.text.split()[0]
    headers = {'User-Agent': str(user_agent.generate_user_agent())}
    htmlContent = requests.get(url, headers=headers)
    await bot.send_message(
        chat_id=update.chat.id,
        text="<code>"+htmlContent+"</code>",
        parse_mode="html",
        disable_web_page_preview=True,
        reply_to_message_id=update.message_id
    )
    
@Clinton.on_message(filters.reply & filters.text)
async def edit_caption(bot, update):
    #logger.info(update)
    await bot.send_cached_media(
        chat_id=update.chat.id,
        file_id=update.reply_to_message.video.file_id,
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
