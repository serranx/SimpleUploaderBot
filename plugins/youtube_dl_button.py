
import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
import asyncio, json, os, time
from datetime import datetime
from config import Config
from translation import Translation
from plugins.custom_thumbnail import *
from helper_funcs.display_progress import progress_for_pyrogram, humanbytes
logging.getLogger("pyrogram").setLevel(logging.WARNING)

async def youtube_dl_call_back(bot, message):
    cb_data = message.data
    tg_send_type, youtube_dl_format, youtube_dl_ext, json_name = cb_data.split("|")
    save_ytdl_json_path = Config.DOWNLOAD_LOCATION + str(message.from_user.id) + "/" + json_name + ".json"
    try:
        with open(save_ytdl_json_path, "r", encoding="utf8") as f:
            response_json = json.load(f)
    except FileNotFoundError as e:
        await bot.delete_messages(
            chat_id=message.message.from_user.id,
            message_ids=message.message.message_id,
            revoke=True
        )
        return
    youtube_dl_url = message.message.reply_to_message.text
    custom_file_name = str(response_json.get("title"))[:60]
    youtube_dl_username = None
    youtube_dl_password = None
    if " * " in youtube_dl_url:
        url_parts = youtube_dl_url.split(" * ")
        if len(url_parts) == 2:
            youtube_dl_url = url_parts[0]
            custom_file_name = url_parts[1]
        elif len(url_parts) == 4:
            youtube_dl_url = url_parts[0]
            custom_file_name = url_parts[1]
            youtube_dl_username = url_parts[2]
            youtube_dl_password = url_parts[3]
        else:
            for entity in message.message.reply_to_message.entities:
                if entity.type == "text_link":
                    youtube_dl_url = entity.url
                elif entity.type == "url":
                    o = entity.offset
                    l = entity.length
                    youtube_dl_url = youtube_dl_url[o:o + l]
        if youtube_dl_url is not None:
            youtube_dl_url = youtube_dl_url.strip()
        if custom_file_name is not None:
            custom_file_name = custom_file_name.strip()
        if youtube_dl_username is not None:
            youtube_dl_username = youtube_dl_username.strip()
        if youtube_dl_password is not None:
            youtube_dl_password = youtube_dl_password.strip()
    else:
        for entity in message.message.reply_to_message.entities:
            if entity.type == "text_link":
                youtube_dl_url = entity.url
            elif entity.type == "url":
                o = entity.offset
                l = entity.length
                youtube_dl_url = youtube_dl_url[o:o + l]
    
    if len(custom_file_name.split(".")) > 1:
        description = custom_file_name.split("." + youtube_dl_ext)[0]
    else:
        description = custom_file_name
    if not "unknown" in youtube_dl_ext and not "." + youtube_dl_ext in custom_file_name:
        custom_file_name += "." + youtube_dl_ext
    logger.info(youtube_dl_url)
    logger.info(custom_file_name)
    
    info_msg = await bot.edit_message_text(
        text=Translation.DOWNLOAD_START.format(custom_file_name),
        chat_id=message.message.from_user.id,
        message_id=message.message.message_id
    )

    tmp_directory_for_each_user = Config.DOWNLOAD_LOCATION + str(message.from_user.id)
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    if "/" in custom_file_name:
        file_mimx = custom_file_name
        file_maix = file_mimx.split("/")
        file_name = " ".join(file_maix)
    else:
        file_name = custom_file_name
    download_directory = tmp_directory_for_each_user + "/" + str(file_name)
    command_to_exec = []
    if tg_send_type == "audio":
        command_to_exec = [
            "yt-dlp",
            "-c",
            "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
            "--prefer-ffmpeg",
            "--extract-audio",
            "--audio-format", youtube_dl_ext,
            "--audio-quality", youtube_dl_format,
            youtube_dl_url,
            "-o", download_directory
        ]
    else:
        # command_to_exec = ["yt-dlp", "-f", youtube_dl_format, "--hls-prefer-ffmpeg", "--recode-video", "mp4", "-k", youtube_dl_url, "-o", download_directory]
        minus_f_format = youtube_dl_format
        if "youtu" in youtube_dl_url:
            minus_f_format = youtube_dl_format + "+bestaudio"
        command_to_exec = [
            "yt-dlp",
            "-c",
            "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
            "--embed-subs",
            "-f", minus_f_format,
            "--hls-prefer-ffmpeg", youtube_dl_url,
            "-o", download_directory
        ]
    if Config.HTTP_PROXY != "":
        command_to_exec.append("--proxy")
        command_to_exec.append(Config.HTTP_PROXY)
    if youtube_dl_username is not None:
        command_to_exec.append("--username")
        command_to_exec.append(youtube_dl_username)
    if youtube_dl_password is not None:
        command_to_exec.append("--password")
        command_to_exec.append(youtube_dl_password)
    command_to_exec.append("--no-warnings")
    # command_to_exec.append("--quiet")
    start = datetime.now()
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
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
        os.remove(save_ytdl_json_path)
        end_one = datetime.now()
        time_taken_for_download = (end_one - start).seconds
        file_size = Config.TG_MAX_FILE_SIZE + 1
        try:
            file_size = os.stat(download_directory).st_size
        except FileNotFoundError as e:
            try:
                _download_directory = tmp_directory_for_each_user + "/" + custom_file_name + "." + "mkv"
                download_directory = tmp_directory_for_each_user + "/" + description + "." + "mkv"
                os.rename(_download_directory, download_directory)
                file_size = os.stat(download_directory).st_size
            except:
                await info_msg.edit_text(
                    Translation.UNKNOWN_ERROR
                )
                return
        if file_size > Config.TG_MAX_FILE_SIZE:
            await info_msg.edit_text(
                Translation.RCHD_TG_API_LIMIT.format(custom_file_name, time_taken_for_download, humanbytes(file_size))
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
                await bot.send_audio(
                    chat_id=message.message.chat.id,
                    audio=download_directory,
                    caption=description,
                    parse_mode="HTML",
                    duration=duration,
                    thumb=thumbnail,
                    reply_to_message_id=message.message.reply_to_message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        message.message,
                        custom_file_name,
                        start_time
                    )
                )
            elif tg_send_type == "file":
                thumbnail = await Gthumb01(bot, message)
                await bot.send_document(
                    chat_id=message.message.chat.id,
                    document=download_directory,
                    thumb=thumbnail,
                    caption=description,
                    parse_mode="HTML",
                    reply_to_message_id=message.message.reply_to_message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        message.message,
                        custom_file_name,
                        start_time
                    )
                )
            elif tg_send_type == "video":
                 width, height, duration = await Mdata01(download_directory)
                 thumbnail = await Gthumb02(bot, message, duration, download_directory)
                 await bot.send_video(
                    chat_id=message.message.chat.id,
                    video=download_directory,
                    caption=description,
                    parse_mode="HTML",
                    duration=duration,
                    width=width,
                    height=height,
                    thumb=thumbnail,
                    supports_streaming=True,
                    reply_to_message_id=message.message.reply_to_message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        message.message,
                        custom_file_name,
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
                Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(time_taken_for_download, time_taken_for_upload),
                disable_web_page_preview=True
            )
            logger.info("✅ " + custom_file_name)
            logger.info("✅ Downloaded in: " + str(time_taken_for_download))
            logger.info("✅ Uploaded in: " + str(time_taken_for_upload))
