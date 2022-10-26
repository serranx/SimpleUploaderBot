
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import os, asyncio, aiohttp, json, math, time
from datetime import datetime
from config import Config
from translation import Translation
from plugins.custom_thumbnail import *
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from helper_funcs.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter

async def download(bot, message):
    cb_data = message.data
    _, tg_send_type, source, json_name = cb_data.split("|")
    save_ytdl_json_path = Config.DOWNLOAD_LOCATION + str(message.message.chat.id) + \
        "/" + json_name + ".json"
    thumb_image_path = Config.DOWNLOAD_LOCATION + str(message.message.chat.id) + \
        "/" + json_name + ".jpg"
    try:
        with open(save_ytdl_json_path, "r", encoding="utf8") as f:
            response_json = json.load(f)
    except Exception as e:
        await bot.send_message(
            chat_id=message.message.chat.id,
            text=str(e)
        )
        return
    youtube_dl_url = response_json[int(source)]["url"]
    youtube_dl_ext = response_json[int(source)]["ext"]
    custom_file_name = response_json[int(source)]["title"]
    if " * " in message.message.reply_to_message.text:
        url_parts = message.message.reply_to_message.text.split(" * ")
        if len(url_parts) >= 2:
            custom_file_name = url_parts[1]
    if not "." + youtube_dl_ext in custom_file_name:
        custom_file_name += '.' + youtube_dl_ext
    description = custom_file_name.split("." + youtube_dl_ext)[0]
    logger.info(youtube_dl_url)
    logger.info(custom_file_name)
    info_msg = await bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        text="<b>Downloading to my server... 📥</b>"
    )
    tmp_directory_for_each_user = Config.DOWNLOAD_LOCATION + str(message.message.chat.id)
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    download_directory = tmp_directory_for_each_user + "/" + custom_file_name
    command_to_exec = []
    async with aiohttp.ClientSession() as session:
        start = datetime.now()
        c_time = time.time()
        try:
            await download_coroutine(
                info_msg,
                session,
                youtube_dl_url,
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
        if os.path.exists(save_ytdl_json_path):
            os.remove(save_ytdl_json_path)
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
                Translation.RCHD_TG_API_LIMIT.format(custom_file_name, time_taken_for_download, humanbytes(file_size))
            )
            os.remove(download_directory)
            return
        else:
            start_time = time.time()
            # try to upload file
            if tg_send_type == "audio":
                duration = await Mdata03(download_directory)
                thumb_image_path = await Gthumb01(bot, message)
                await message.message.reply_to_message.reply_audio(
                    audio=download_directory,
                    caption=description,
                    duration=duration,
                    thumb=thumb_image_path,
                    quote=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        info_msg,
                        custom_file_name,
                        start_time
                    )
                )
            elif tg_send_type == "file":
                thumb_image_path = await Gthumb01(bot, message)
                await message.message.reply_to_message.reply_document(
                    document=download_directory,
                    thumb=thumb_image_path,
                    caption=description,
                    quote=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        info_msg,
                        custom_file_name,
                        start_time
                    )
                )
            elif tg_send_type == "video":
                width, height, duration = await Mdata01(download_directory)
                thumb_image_path = await Gthumb02(bot, message, duration, download_directory)
                await message.message.reply_to_message.reply_video(
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
                        custom_file_name,
                        start_time
                    )
                )
            else:
                logger.info("Did this happen? :\\")
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
            logger.info("✅ " + custom_file_name)
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
                            TimeFormatter(time_to_completion) if time_to_completion != "" else "0s"
                        )
                        if current_message != display_message:
                            await info_msg.edit_text(
                                current_message + "\n\n<i><b>Note:</b> fembed links are very low, so be patient.</i>"
                            )
                            display_message = current_message
                            #time.sleep(4.25)
                    except Exception as e:
                        #logger.info(str(e))
                        pass
        return await response.release()
