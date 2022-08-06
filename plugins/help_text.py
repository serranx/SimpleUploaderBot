
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import re

from config import Config
# the Strings used for this "thing"
from translation import Translation

from pyrogram import filters
from database.adduser import AddUser
from pyrogram import Client as Clinton
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from . import mediafire
from . import fembed
#from . import dl_button
import lk21

@Clinton.on_message(filters.private & filters.command(["test"]))
async def test(bot, update):
    path = Config.DOWNLOAD_LOCATION + "/" + str(update.chat.id) + "/"
    try:
        files = os.listdir(path)
        joined_files = "\n".join(files)
        print(joined_files)
        await bot.send_message(
            chat_id=update.chat.id,
            text=str(joined_files),
            parse_mode="html",
            reply_to_message_id=update.message_id
        )
    except:
        await bot.send_message(
            chat_id=update.chat.id,
            text="No files found.",
            parse_mode="html",
            reply_to_message_id=update.message_id
        )
    """
    msg_info = await bot.send_message(
        chat_id=update.chat.id,
        text="Test message...",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "Cancel",
                    callback_data="cancel|abcd"
                ),
            ],
        ]),
        parse_mode="html",
        reply_to_message_id=update.message_id
    )
    """

@Clinton.on_message(filters.regex(pattern="fembed\.com|fembed-hd\.com|femax20\.com|vanfem\.com|suzihaza\.com|embedsito\.com|owodeuwu\.xyz|plusto\.link"))
async def dl_fembed(bot, update):
    processing = await update.reply_text("<b>Processing... ⏳</b>", reply_to_message_id=update.message_id)
    
    bypasser = lk21.Bypass()
    source = -1
    if " * " in update.text:
        if len(update.text.split(" * ")) == 3:
            source = int(update.text.split(" * ")[2]) - 1
        url = update.text.split(" * ")[0]
        url = "https://fembed.com/f/" + url.split("/")[-1]
        """
        if "www." in url:
            url = url.split("www.")[0] + url.split("www.")[1]
        """
    else:
        url = update.text
        url = "https://fembed.com/f/" + url.split("/")[-1]
        """
        if "www." in url:
            url = url.split("www.")[0] + url.split("www.")[1]
        """
    json = bypasser.bypass_url(url)
    formats = {
        "formats": []
    }
    try:
        for format in json:
            aux = {
                "ext": format["key"].split("/")[1],
                "format_id": format["key"].split("/")[0],
                "format": format["key"].split("/")[0],
                "url": format["value"]
            }
            formats["formats"].append(aux)
    except:
        await bot.send_message(
            chat_id=update.chat.id,
            text="Invalid link!",
            reply_to_message_id=update.message_id,
            parse_mode="html",
            disable_web_page_preview=True
        )
    await processing.delete(True)
    await fembed.download(bot, update, formats, source)
    
@Clinton.on_message(filters.regex(pattern="\.mediafire\.com/"))
async def dl_mediafire(bot, update):
    video_formats = ["mp4", "mkv", "webm", "avi", "wmv", "mov"]
    audio_formats = ["mp3", "m4a"]
    processing = await update.reply_text("<b>Processing... ⏳</b>", reply_to_message_id=update.message_id)
    if " * " in update.text:
      try:
        url, custom_filename = update.text.split(" * ")
      except:
        await bot.edit_message_text(
          text=Translation.INCORRECT_REQUEST,
          chat_id=update.chat.id,
          message_id=processing.message_id
        )
      if re.search("download[0-9]*\.mediafire\.com", url):
        url_parts = url.split("/")
        url = "https://www.mediafire.com/file/" + url_parts[-2] + "/" + url_parts[-1] + "/file"
      r = await mediafire.get(url)
      dl_link, filename = r.split("|")
      dl_ext = filename.split(".")[-1]
      filename = custom_filename
    else:
      url = update.text
      if re.search("download[0-9]*\.mediafire\.com", url):
        url_parts = url.split("/")
        url = "https://www.mediafire.com/file/" + url_parts[-2] + "/" + url_parts[-1] + "/file"
      r = await mediafire.get(url)
      dl_link, filename = r.split("|")
      dl_ext = filename.split(".")[-1]
    if dl_ext in video_formats:
      send_type = "video"
    elif dl_ext in audio_formats:
      send_type = "audio"
    else:
      send_type = "file"
    update.data = "{}|{}|{}|{}".format(send_type, dl_link, dl_ext, filename)
    await processing.delete(True)
    await mediafire.download(bot, update)

@Clinton.on_message(filters.private & filters.command(["cancel"]))
async def cancel_process(bot, update):
    save_ytdl_json_path = Config.DOWNLOAD_LOCATION + "/" + str(update.chat.id) + ".json"
    if os.path.exists(save_ytdl_json_path):
        os.remove(save_ytdl_json_path)
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.PROCESS_CANCELLED,
            parse_mode="html",
            disable_web_page_preview=True,
            reply_to_message_id=update.message_id
        )
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.NO_PROCESS_FOUND,
            parse_mode="html",
            disable_web_page_preview=True,
            reply_to_message_id=update.message_id
        )

@Clinton.on_message(filters.private & filters.reply & filters.text)
async def edit_caption(bot, update):
    try:
        await bot.send_cached_media(
            chat_id=update.chat.id,
            file_id=update.reply_to_message.video.file_id,
            reply_to_message_id=update.message_id,
            caption=update.text
        )
    except:
        try:
            await bot.send_cached_media(
                chat_id=update.chat.id,
                file_id=update.reply_to_message.document.file_id,
                reply_to_message_id=update.message_id,
                caption=update.text
            )
        except:
            pass

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
                    InlineKeyboardButton("Source code ⚡", url="https://github.com/wywxz/SimpleUploaderBot"),
                    InlineKeyboardButton("Developer 👨‍⚖️", url="https://t.me/SimpleBotsX"),
                ],
            ]
        ),
        reply_to_message_id=update.message_id
    )
