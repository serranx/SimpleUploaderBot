
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import random, os, time
from PIL import Image
from config import Config
from translation import Translation
from pyrogram import Client
from database.access import clinton
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram import filters
from database.adduser import AddUser
from helper_funcs.help_Nekmo_ffmpeg import take_screen_shot

@Client.on_message(filters.private & filters.photo)
async def save_photo(bot, message):
    await AddUser(bot, message)
    await clinton.set_thumbnail(message.from_user.id, thumbnail=message.photo.file_id)
    await message.reply_text(
        Translation.SAVED_CUSTOM_THUMB_NAIL,
        quote=True
    )

@Client.on_message(filters.private & filters.command("delthumbnail"))
async def delthumbnail(bot, message):
    await AddUser(bot, message)
    thumbnail = await clinton.get_thumbnail(message.from_user.id)
    if thumbnail is not None:
        await clinton.set_thumbnail(message.from_user.id, thumbnail=None)
        await message.reply_text(
            Translation.DEL_ETED_CUSTOM_THUMB_NAIL,
            quote=True
        )
    else:
        await message.reply_text(
            "Nothing to delete 🤨",
            quote=True
        )

@Client.on_message(filters.private & filters.command("viewthumbnail") )
async def viewthumbnail(bot, message):
    await AddUser(bot, message)
    thumbnail = await clinton.get_thumbnail(message.from_user.id)
    if thumbnail is not None:
        await message.reply_photo(
            photo=thumbnail,
            caption="Your current saved thumbnail 😊",
            quote=True
        )
    else:
        await message.reply_text(
            "No thumbnail found 🥴",
            quote=True
        )

async def Gthumb01(bot, message):
    thumb_image_path = Config.DOWNLOAD_LOCATION + str(message.from_user.id) + ".jpg"
    db_thumbnail = await clinton.get_thumbnail(message.from_user.id)
    if db_thumbnail is not None:
        thumbnail = await bot.download_media(message=db_thumbnail, file_name=thumb_image_path)
        Image.open(thumbnail).convert("RGB").save(thumbnail)
        img = Image.open(thumbnail)
        img.resize((100, 100))
        img.save(thumbnail, "JPEG")
    else:
        thumbnail = None
    return thumbnail

async def Gthumb02(bot, message, duration, download_directory):
    thumb_image_path = Config.DOWNLOAD_LOCATION + str(message.from_user.id) + ".jpg"
    db_thumbnail = await clinton.get_thumbnail(message.from_user.id)
    if duration == 0:
        duration = 1
    if db_thumbnail is not None:
        thumbnail = await bot.download_media(message=db_thumbnail, file_name=thumb_image_path)
    else:
        thumbnail = await take_screen_shot(download_directory, os.path.dirname(download_directory), random.randint(0, duration - 1))
    return thumbnail

async def Mdata01(download_directory):
    width = 0
    height = 0
    duration = 0
    metadata = extractMetadata(createParser(download_directory))
    if metadata is not None:
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds
        if metadata.has("width"):
            width = metadata.get("width")
        if metadata.has("height"):
            height = metadata.get("height")
    return width, height, duration

async def Mdata02(download_directory):
    width = 0
    duration = 0
    metadata = extractMetadata(createParser(download_directory))
    if metadata is not None:
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        if metadata.has("width"):
            width = metadata.get("width")
    return width, duration

async def Mdata03(download_directory):
    duration = 0
    metadata = extractMetadata(createParser(download_directory))
    if metadata is not None:
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
    return duration
