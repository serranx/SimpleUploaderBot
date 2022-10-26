
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import os, time, asyncio, json
from config import Config
from datetime import datetime
from translation import Translation
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from helper_funcs.display_progress import humanbytes
from helper_funcs.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from plugins.custom_thumbnail import *

async def get(url):
    if Config.HTTP_PROXY != "":
        command_to_exec = [
            "yt-dlp",
            "--no-warnings",
            "--youtube-skip-dash-manifest",
            "-j",
            url,
            "--proxy", Config.HTTP_PROXY
        ]
    else:
        command_to_exec = [
            "yt-dlp",
            "--no-warnings",
            "--youtube-skip-dash-manifest",
            "-j",
            url
        ]
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    
    x_reponse = t_response
    if "\n" in x_reponse:
        x_reponse, _ = x_reponse.split("\n")
    response_json = json.loads(x_reponse)
    title = response_json["title"]
    response_json = response_json["formats"][-1]
    response_json["title"] = title
    return response_json
        
async def download(bot, message, info_msg):
    cb_data = message.data
    tg_send_type, youtube_dl_url, filename = cb_data.split("|")
    description = filename.split("." + filename.split(".")[-1])[0]
    await info_msg.edit_text(
        Translation.DOWNLOAD_START.format(filename)
    )
    tmp_directory_for_each_user = Config.DOWNLOAD_LOCATION + str(message.chat.id)
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    download_directory = tmp_directory_for_each_user + "/" + filename
    command_to_exec = [
        "yt-dlp",
        "-c",
        "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
        "--embed-subs",
        "-f", "source",
        "--hls-prefer-ffmpeg", youtube_dl_url,
        "-o", download_directory
    ]
    if Config.HTTP_PROXY != "":
        command_to_exec.append("--proxy")
        command_to_exec.append(Config.HTTP_PROXY)
    command_to_exec.append("--no-warnings")
    start = datetime.now()
    try:
        process = await asyncio.create_subprocess_exec(
            *command_to_exec,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except Exception as e:
        await message.reply_text(
            str(e)
        )
        return
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    ad_string_to_replace = "please report this issue on  https://github.com/yt-dlp/yt-dlp/issues?q= , filling out the appropriate issue template. Confirm you are on the latest version using  yt-dlp -U"
    if e_response and ad_string_to_replace in e_response:
        error_message = e_response.replace(ad_string_to_replace, "")
        await info_msg.edit_text(
            error_message
        )
        return
    if t_response:
        end_one = datetime.now()
        time_taken_for_download = (end_one - start).seconds
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
            await info_msg.edit_text(
                Translation.UPLOAD_START
            )
            start_time = time.time()
            # try to upload file
            if tg_send_type == "audio":
                duration = await Mdata03(download_directory)
                thumbnail = await Gthumb01(bot, message)
                await message.reply_audio(
                    audio=download_directory,
                    caption=description,
                    duration=duration,
                    thumb=thumbnail,
                    quote=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        info_msg,
                        filename,
                        start_time
                    )
                )
            elif tg_send_type == "file":
                thumbnail = await Gthumb01(bot, message)
                await message.reply_document(
                    document=download_directory,
                    thumb=thumbnail,
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
            elif tg_send_type == "video":
                width, height, duration = await Mdata01(download_directory)
                thumbnail = await Gthumb02(bot, message, duration, download_directory)
                await message.reply_video(
                    video=download_directory,
                    caption=description,
                    duration=duration,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    thumb=thumbnail,
                    quote=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        info_msg,
                        filename,
                        start_time
                    )
                )
            else:
                logger.info("Did this happen? :\\")
            end_two = datetime.now()
            time_taken_for_upload = (end_two - end_one).seconds
            try:
                os.remove(download_directory)
                os.remove(thumbnail)
            except:
                pass
            await info_msg.edit_text(
                Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(time_taken_for_download, time_taken_for_upload)
            )
            logger.info("✅ " + filename)
            logger.info("✅ Downloaded in: " + str(time_taken_for_download))
            logger.info("✅ Uploaded in: " + str(time_taken_for_upload))
