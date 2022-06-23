#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K | X-Noid | @DC4_WARRIOR

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import sys, requests, urllib.parse, filetype, os, time, shutil, tldextract, asyncio, json, math

from config import Config
from database.adduser import AddUser
from translation import Translation
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram import filters
from pyrogram import Client as Clinton
from database.access import clinton
from helper_funcs.display_progress import humanbytes
from helper_funcs.help_uploadbot import DownLoadFile
from helper_funcs.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

async def download(bot, update, formats):
    #imog = await update.reply_text("<b>Processing... ⏳</b>", reply_to_message_id=update.message_id)
    """
    if os.path.exists(Config.DOWNLOAD_LOCATION + "/" + str(update.chat.id) + ".json"):
        await bot.edit_message_text(
            text=Translation.WAIT_PROCESS_FINISH,
            chat_id=update.chat.id,
            message_id=imog.message_id
        )
        return False
    """
    file_name = None
    url = update.text
    if " * " in url:
        url_parts = url.split(" * ")
        if len(url_parts) == 2:
            file_name = url_parts[1]
        if file_name is not None:
            file_name = file_name.strip()
    """
    await bot.edit_message_text(
        text="<b>Processing... ⌛</b>",
        chat_id=update.chat.id,
        message_id=update.message.message_id
    )
    time.sleep(1)
    """
    if formats:
        x_reponse = formats
        if "\n" in x_reponse:
            x_reponse, _ = x_reponse.split("\n")
        response_json = json.loads(x_reponse)
        save_ytdl_json_path = Config.DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + ".json"
        with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
            json.dump(response_json, outfile, ensure_ascii=False)
        # logger.info(response_json)
        inline_keyboard = []
        duration = None
        if "duration" in response_json:
            duration = response_json["duration"]
        if "formats" in response_json:
            for formats in response_json["formats"]:
                format_id = formats.get("format_id")
                format_string = formats.get("format_note")
                if format_string is None:
                    format_string = formats.get("format")
                format_ext = formats.get("ext")
                approx_file_size = ""
                if "filesize" in formats:
                    approx_file_size = humanbytes(formats["filesize"])
                cb_string_video = "{}|{}|{}".format(
                    "video", format_id, format_ext)
                cb_string_file = "{}|{}|{}".format(
                    "file", format_id, format_ext)
                if format_string is not None and not "audio only" in format_string:
                    if len(format_string.split("-")) > 1:
                        echo_vid = "🎥 video " + format_string.split("-")[0] + " " + approx_file_size
                    else:
                        echo_vid = "🎥 video " + format_ext + " " + approx_file_size
                    ikeyboard = [
                        InlineKeyboardButton(
                            echo_vid,
                            callback_data=(cb_string_video).encode("UTF-8")
                        ),
                        InlineKeyboardButton(
                            "📄 file " + format_ext + " " + approx_file_size,
                            callback_data=(cb_string_file).encode("UTF-8")
                        )
                    ]
                    """if duration is not None:
                        cb_string_video_message = "{}|{}|{}".format(
                            "vm", format_id, format_ext)
                        ikeyboard.append(
                            InlineKeyboardButton(
                                "VM",
                                callback_data=(
                                    cb_string_video_message).encode("UTF-8")
                            )
                        )"""
                else:
                    # special weird case :\
                    ikeyboard = [
                        InlineKeyboardButton(
                            "🎥 video - " + format_ext,
                            callback_data=(cb_string_video).encode("UTF-8")
                        ),
                        InlineKeyboardButton(
                            "📄 file - " + format_ext,
                            callback_data=(cb_string_file).encode("UTF-8")
                        )
                    ]
                inline_keyboard.append(ikeyboard)
            if duration is not None:
                cb_string_64 = "{}|{}|{}".format("audio", "64k", "mp3")
                cb_string_128 = "{}|{}|{}".format("audio", "128k", "mp3")
                cb_string = "{}|{}|{}".format("audio", "320k", "mp3")
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "🎧 MP3 " + "(" + "64 kbps" + ")", callback_data=cb_string_64.encode("UTF-8")),
                    InlineKeyboardButton(
                        "🎧 MP3 " + "(" + "128 kbps" + ")", callback_data=cb_string_128.encode("UTF-8"))
                ])
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "🎧 MP3 " + "(" + "320 kbps" + ")", callback_data=cb_string.encode("UTF-8"))
                ])
        else:
            format_id = response_json["format_id"]
            format_ext = response_json["ext"]
            cb_string_file = "{}|{}|{}".format(
                "file", format_id, format_ext)
            cb_string_video = "{}|{}|{}".format(
                "video", format_id, format_ext)
            inline_keyboard.append([
                InlineKeyboardButton(
                    "🎥 video - " + format_ext,
                    callback_data=(cb_string_video).encode("UTF-8")
                ),
                InlineKeyboardButton(
                    "📄 file - " + format_ext,
                    callback_data=(cb_string_file).encode("UTF-8")
                )
            ])
            cb_string_file = "{}={}={}".format(
                "file", format_id, format_ext)
            cb_string_video = "{}={}={}".format(
                "video", format_id, format_ext)
            inline_keyboard.append([
                InlineKeyboardButton(
                    "🎥 video - " + format_ext,
                    callback_data=(cb_string_video).encode("UTF-8")
                ),
                InlineKeyboardButton(
                    "📃 file - " + format_ext,
                    callback_data=(cb_string_file).encode("UTF-8")
                )
            ])
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FORMAT_SELECTION,
            reply_markup=reply_markup,
            parse_mode="html",
            reply_to_message_id=update.message_id
        )
    else:
        # fallback for nonnumeric port a.k.a seedbox.io
        inline_keyboard = []
        cb_string_file = "{}={}={}".format(
            "file", "LFO", "NONE")
        cb_string_video = "{}={}={}".format(
            "video", "OFL", "ENON")
        inline_keyboard.append([
            InlineKeyboardButton(
                "🎥 video",
                callback_data=(cb_string_video).encode("UTF-8")
            ),
            InlineKeyboardButton(
                "📄 file",
                callback_data=(cb_string_file).encode("UTF-8")
            )
        ])
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FORMAT_SELECTION,
            reply_markup=reply_markup,
            parse_mode="html",
            reply_to_message_id=update.message_id
        )
