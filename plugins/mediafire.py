
import requests
import asyncio
import aiohttp
import os
import time
from datetime import datetime
from bs4 import BeautifulSoup
# the secret configuration specific things
from config import Config
# the Strings used for this "thing"
from translation import Translation
from plugins.custom_thumbnail import *
from helper_funcs.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

async def get(url):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }
    
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    
    dl_url = soup.find("a", class_="popsok").get('href')
    filename = soup.find("div", class_="filename").get_text()
    
    return "{}|{}".format(dl_url, filename)
    
async def download(bot, update):
    cb_data = update.data
    send_type, dl_link, ext, filename = cb_data.split("|")
    print(update)
    start = datetime.now()
    dl_info = await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.DOWNLOAD_START.format(filename),
        parse_mode="html",
        disable_web_page_preview=True,
        reply_to_message_id=update.message_id
    )
    tmp_directory_for_each_user = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id)
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    download_directory = tmp_directory_for_each_user + "/" + filename
    command_to_exec = []
    async with aiohttp.ClientSession() as session:
        c_time = time.time()
        try:
            await download_coroutine(
                bot,
                session,
                dl_link,
                download_directory,
                update.chat.id,
                update.message_id,
                c_time
            )
        except asyncio.TimeoutError:
            await bot.edit_message_text(
                text=Translation.SLOW_URL_DECED,
                chat_id=update.chat.id,
                message_id=update.message_id
            )
            return False
    if os.path.exists(download_directory):
        end_one = datetime.now()
        time_taken_for_download = (end_one - start).seconds
        await bot.edit_message_text(
            text=Translation.UPLOAD_START,
            chat_id=update.chat.id,
            message_id=dl_info.message_id
        )
        file_size = Config.TG_MAX_FILE_SIZE + 1
        try:
            file_size = os.stat(download_directory).st_size
        except FileNotFoundError as exc:
            download_directory = os.path.splitext(download_directory)[0] + "." + "mkv"
            # https://stackoverflow.com/a/678242/4723940
            file_size = os.stat(download_directory).st_size
        if file_size > Config.TG_MAX_FILE_SIZE:
            await bot.edit_message_text(
                chat_id=update.chat.id,
                text=Translation.RCHD_TG_API_LIMIT.format(time_taken_for_download, humanbytes(file_size)),
                message_id=dl_info.message_id
            )
        else:
            # ref: message from @SOURCES_CODES
            start_time = time.time()
            # try to upload file
            if send_type == "audio":
                duration = await Mdata03(download_directory)
                thumb_image_path = await Gthumb01(bot, update)
                await bot.send_audio(
                    chat_id=update.chat.id,
                    audio=download_directory,
                    caption=filename,
                    duration=duration,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        dl_info,
                        start_time
                    )
                )
            elif send_type == "file":
                  thumb_image_path = await Gthumb01(bot, update)
                  await bot.send_document(
                    chat_id=update.chat.id,
                    document=download_directory,
                    thumb=thumb_image_path,
                    caption=filename,
                    reply_to_message_id=update.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        dl_info,
                        start_time
                    )
                )
            elif send_type == "vm":
                 width, duration = await Mdata02(download_directory)
                 thumb_image_path = await Gthumb02(bot, update, duration, download_directory)
                 await bot.send_video_note(
                    chat_id=update.chat.id,
                    video_note=download_directory,
                    duration=duration,
                    length=width,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        dl_info,
                        start_time
                    )
                )
            elif send_type == "video":
                 width, height, duration = await Mdata01(download_directory)
                 thumb_image_path = await Gthumb02(bot, update, duration, download_directory)
                 await bot.send_video(
                    chat_id=update.chat.id,
                    video=download_directory,
                    caption=filename,
                    duration=duration,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        dl_info,
                        start_time
                    )
                )
            end_two = datetime.now()
            try:
                os.remove(download_directory)
                os.remove(thumb_image_path)
            except:
                pass
            time_taken_for_upload = (end_two - end_one).seconds
            await bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(time_taken_for_download, time_taken_for_upload),
                chat_id=update.chat.id,
                message_id=dl_info.message_id,
                disable_web_page_preview=True
            )
            print(dl_info)
            logger.info("✅ " + filename)
            logger.info("✅ Downloaded in: " + str(time_taken_for_download))
            logger.info("✅ Uploaded in: " + str(time_taken_for_upload))
    else:
        await bot.edit_message_text(
            text=Translation.NO_VOID_FORMAT_FOUND.format("Incorrect Link"),
            chat_id=update.chat.id,
            message_id=dl_info.message_id,
            disable_web_page_preview=True
        )

async def download_coroutine(bot, session, url, file_name, chat_id, message_id, start):
    downloaded = 0
    display_message = ""
    async with session.get(url, timeout=Config.PROCESS_MAX_TIMEOUT) as response:
        total_length = int(response.headers["Content-Length"])
        content_type = response.headers["Content-Type"]
        if "text" in content_type and total_length < 500:
            return await response.release()
        
        with open(file_name, "wb") as f_handle:
            while True:
                chunk = await response.content.read(Config.CHUNK_SIZE)
                if not chunk:
                    break
                f_handle.write(chunk)
                downloaded += Config.CHUNK_SIZE
                now = time.time()
                diff = now - start
                if round(diff % 5.00) == 0 or downloaded == total_length:
                    percentage = downloaded * 100 / total_length
                    speed = downloaded / diff
                    elapsed_time = round(diff) * 1000
                    time_to_completion = round((total_length - downloaded) / speed) * 1000
                    estimated_total_time = elapsed_time + time_to_completion
        return await response.release()
    