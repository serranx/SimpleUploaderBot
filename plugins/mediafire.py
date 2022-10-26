
import os, requests, asyncio, aiohttp, time, math
from datetime import datetime
from bs4 import BeautifulSoup
from config import Config
from translation import Translation
from plugins.custom_thumbnail import *
from helper_funcs.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter

async def get(url):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "3600",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
    }
    req = requests.get(url, stream=True)
    soup = BeautifulSoup(req.content, "html.parser")
    dl_url = soup.find("a", id="downloadButton").get("href")
    try:
        filename = soup.find("div", class_="filename").get_text()
    except:
        filename = soup.find("div", class_="dl-btn-label").get("title")
    return dl_url, filename
    
async def download(bot, message, info_msg):
    cb_data = message.data
    send_type, dl_url, filename = cb_data.split("|")
    description = filename.split("." + filename.split(".")[-1])[0]
    tmp_directory_for_each_user = Config.DOWNLOAD_LOCATION + str(message.from_user.id)
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    download_directory = tmp_directory_for_each_user + "/" + filename
    command_to_exec = []
    async with aiohttp.ClientSession() as session:
        start = datetime.now()
        c_time = time.time()
        try:
            await download_coroutine(
                info_msg,
                session,
                dl_url,
                download_directory,
                c_time
            )
        except asyncio.TimeoutError:
            await info_msg.edit_text(
                Translation.SLOW_URL_DECED
            )
            return
    if os.path.exists(download_directory):
        end_one = datetime.now()
        time_taken_for_download = (end_one - start).seconds
        await info_msg.edit_text(
            Translation.UPLOAD_START
        )
        file_size = Config.TG_MAX_FILE_SIZE + 1
        try:
            file_size = os.stat(download_directory).st_size
        except FileNotFoundError as exc:
            download_directory = os.path.splitext(download_directory)[0] + "." + "mkv"
            file_size = os.stat(download_directory).st_size
        if file_size > Config.TG_MAX_FILE_SIZE:
            await info_msg.edit_text(
                Translation.RCHD_TG_API_LIMIT.format(filename, time_taken_for_download, humanbytes(file_size))
            )
            os.remove(download_directory)
            return
        else:
            start_time = time.time()
            # try to upload file
            if send_type == "audio":
                duration = await Mdata03(download_directory)
                thumb_image_path = await Gthumb01(bot, message)
                await message.reply_audio(
                    audio=download_directory,
                    caption=description,
                    duration=duration,
                    thumb=thumb_image_path,
                    quote=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        info_msg,
                        filename,
                        start_time
                    )
                )
            elif send_type == "file":
                thumb_image_path = await Gthumb01(bot, message)
                await message.reply_document(
                    document=download_directory,
                    thumb=thumb_image_path,
                    caption=description,
                    quote=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        info_msg,
                        filename,
                        start_time
                    )
                )
            elif send_type == "video":
                width, height, duration = await Mdata01(download_directory)
                thumb_image_path = await Gthumb02(bot, message, duration, download_directory)
                await message.reply_video(
                    video=download_directory,
                    caption=description,
                    duration=duration,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    thumb=thumb_image_path,
                    quote=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        info_msg,
                        filename,
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
            await info_msg.edit_text(
                Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(time_taken_for_download, time_taken_for_upload)
            )
            logger.info("✅ " + filename)
            logger.info("✅ Downloaded in: " + str(time_taken_for_download))
            logger.info("✅ Uploaded in: " + str(time_taken_for_upload))
    else:
        await info_msg.edit_text(
            Translation.NO_VOID_FORMAT_FOUND.format("Incorrect Link"),
            disable_web_page_preview=True
        )

async def download_coroutine(info_msg, session, url, file_name, start):
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
                    try:
                        current_message = "<b>Downloading to my server... 📥</b>\n" + Translation.DISPLAY_PROGRESS.format(
                            "".join(["●" for i in range(math.floor(percentage / 5))]),
                            "".join(["○" for i in range(20 - math.floor(percentage / 5))]),
                            round(percentage, 2),
                            file_name.split("/")[-1],
                            humanbytes(downloaded),
                            humanbytes(total_length),
                            humanbytes(speed),
                            TimeFormatter(time_to_completion) if time_to_completion != "" else "0 s"
                        )
                        if current_message != display_message:
                            await info_msg.edit_text(
                                current_message
                            )
                            display_message = current_message
                    except Exception as e:
                        #logger.info(str(e))
                        pass
        return await response.release()
