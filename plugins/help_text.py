
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import os
from config import Config
from translation import Translation
from pyrogram import filters
from database.adduser import AddUser
from pyrogram import Client as Clinton
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@Clinton.on_message(filters.private & filters.command(["files"]))
async def test(bot, message):
    if message.from_user.id != Config.OWNER_ID:
        return
    if len(message.text.split(" ")) == 2:
        user_id = message.text.split(" ")[1]
        if user_id == "me":
            user_id == Config.OWNER_ID
        path = Config.DOWNLOAD_LOCATION + str(user_id) + "/"
        try:
            files = os.listdir(path)
            joined_files = "\n".join(files)
            await message.reply_text(
                str(joined_files),
                quote=True
            )
        except:
            await message.reply_text(
                "No files found.",
                quote=True
            )
            return
    else:
        path = Config.DOWNLOAD_LOCATION
        try:
            files = os.listdir(path)
            joined_files = "\n".join(files)
            await message.reply_text(
                str(joined_files),
                quote=True
            )
        except:
            await message.reply_text(
                "No files found.",
                quote=True
            )
            return

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
                file_id=update.reply_to_message.audio.file_id,
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
    await AddUser(bot, update)
    await update.reply_text(
        Translation.HELP_USER,
        quote=True
    )

@Clinton.on_message(filters.private & filters.command(["addcaption"]))
async def add_caption_help(bot, update):
    await AddUser(bot, update)
    await update.reply_text(
        Translation.ADD_CAPTION_HELP,
        quote=True
    )

@Clinton.on_message(filters.private & filters.command(["start"]))
async def start(bot, update):
    await AddUser(bot, update)
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.START_TEXT.format(update.from_user.first_name),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Source code ⚡", url="https://github.com/wywxz/SimpleUploaderBot"),
                    InlineKeyboardButton("Developer 👨‍⚖️", url="https://t.me/SimpIeBots"),
                ],
            ]
        ),
        reply_to_message_id=update.message_id
    )
