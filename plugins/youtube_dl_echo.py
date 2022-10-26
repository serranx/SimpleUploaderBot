
import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
import os, re, time, asyncio, json, random, string
from config import Config
from database.adduser import AddUser
from translation import Translation
from pyrogram import filters
from pyrogram import Client
from helper_funcs.display_progress import humanbytes, ContentLength
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
logging.getLogger("pyrogram").setLevel(logging.WARNING)

@Client.on_message(filters.regex(pattern=".*http.*"))
async def echo(bot, message):
    await AddUser(bot, message)
    info_msg = await message.reply_text("<b>Processing... ⏳</b>", quote=True)
    youtube_dl_username = None
    youtube_dl_password = None
    file_name = None
    url = message.text
    if " * " in url:
        url_parts = url.split(" * ")
        if len(url_parts) == 2:
            url = url_parts[0]
            file_name = url_parts[1]
        elif len(url_parts) == 4:
            url = url_parts[0]
            file_name = url_parts[1]
            youtube_dl_username = url_parts[2]
            youtube_dl_password = url_parts[3]
        else:
            for entity in message.entities:
                if entity.type == "text_link":
                    url = entity.url
                elif entity.type == "url":
                    o = entity.offset
                    l = entity.length
                    url = url[o:o + l]
        if url is not None:
            url = url.strip()
        if file_name is not None:
            file_name = file_name.strip()
        # https://stackoverflow.com/a/761825/4723940
        if youtube_dl_username is not None:
            youtube_dl_username = youtube_dl_username.strip()
        if youtube_dl_password is not None:
            youtube_dl_password = youtube_dl_password.strip()
    else:
        for entity in message.entities:
            if entity.type == "text_link":
                url = entity.url
            elif entity.type == "url":
                o = entity.offset
                l = entity.length
                url = url[o:o + l]
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
    if youtube_dl_username is not None:
        command_to_exec.append("--username")
        command_to_exec.append(youtube_dl_username)
    if youtube_dl_password is not None:
        command_to_exec.append("--password")
        command_to_exec.append(youtube_dl_password)
    # logger.info(command_to_exec)
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    await info_msg.edit_text("<b>Processing... ⌛</b>")
    time.sleep(0.5)
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    # https://github.com/rg3/youtube-dl/issues/2630#issuecomment-38635239
    if e_response and "nonnumeric port" not in e_response:
        error_message = e_response.replace("please report this issue on  https://github.com/yt-dlp/yt-dlp/issues?q= , filling out the appropriate issue template. Confirm you are on the latest version using  yt-dlp -U", "")
        if "This video is only available for registered users." in error_message:
            error_message += Translation.SET_CUSTOM_USERNAME_PASSWORD
        await info_msg.edit_text(
            Translation.NO_VOID_FORMAT_FOUND.format(str(error_message)),
            disable_web_page_preview=True
        )
        return
    if t_response:
        x_reponse = t_response
        if "\n" in x_reponse:
            x_reponse, _ = x_reponse.split("\n")
        response_json = json.loads(x_reponse)
        json_name = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        tmp_directory_for_each_user = Config.DOWNLOAD_LOCATION + str(message.from_user.id)
        if not os.path.isdir(tmp_directory_for_each_user):
            os.makedirs(tmp_directory_for_each_user)
        save_ytdl_json_path = tmp_directory_for_each_user + "/" + json_name + ".json"
        with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
            json.dump(response_json, outfile, ensure_ascii=False)
        inline_keyboard = []
        duration = None
        if "duration" in response_json:
            duration = response_json["duration"]
        if "formats" in response_json:
            for formats in response_json["formats"]:
                format_id = formats.get("format_id")
                format_string = formats.get("format_note")
                format_ext = formats.get("ext")
                approx_file_size = ""
                if format_string is None:
                    format_string = formats.get("format")
                if "filesize" in formats:
                    approx_file_size = humanbytes(formats["filesize"])
                if "x-matroska" in format_string:
                    format_string = "mkv"
                if "unknown" in format_string:
                    format_string = format_ext
                cb_string_video = "{}|{}|{}|{}".format(
                    "video", format_id, format_ext, json_name)
                cb_string_file = "{}|{}|{}|{}".format(
                    "file", format_id, format_ext, json_name)
                if format_string is not None and not "audio only" in format_string:
                    if format_string == "" or format_string == " " or "DASH" in format_string:
                        continue
                    if re.match("(http(s)?):\/\/(www\.)?youtu(be)?\.(com|be)", url) and re.match("storyboard|ultralow|low|medium", format_string):
                        continue
                    if format_ext in Config.VIDEO_FORMATS:
                        ikeyboard = [
                            InlineKeyboardButton(
                                "🎥 video " + format_string.split("-")[-1] + " " + approx_file_size,
                                callback_data=(cb_string_video).encode("UTF-8")
                            ),
                            InlineKeyboardButton(
                                "📄 file " + format_ext + " " + approx_file_size,
                                callback_data=(cb_string_file).encode("UTF-8")
                            )
                        ]
                    elif format_ext in Config.AUDIO_FORMATS:
                        ikeyboard = [
                            InlineKeyboardButton(
                                "🎧 audio " + format_ext + " " + approx_file_size,
                                callback_data=(cb_string_video).encode("UTF-8")
                            ),
                            InlineKeyboardButton(
                                "📄 file " + format_ext + " " + approx_file_size,
                                callback_data=(cb_string_file).encode("UTF-8")
                            )
                        ]
                    else:
                        ikeyboard = [
                            InlineKeyboardButton(
                                "📄 file " + format_ext + " " + approx_file_size,
                                callback_data=(cb_string_file).encode("UTF-8")
                            )
                        ]
                    inline_keyboard.append(ikeyboard)
            if duration is not None:
                cb_string_64 = "{}|{}|{}|{}".format("audio", "64k", "mp3", json_name)
                cb_string_128 = "{}|{}|{}|{}".format("audio", "128k", "mp3", json_name)
                cb_string = "{}|{}|{}|{}".format("audio", "320k", "mp3", json_name)
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "🎧 MP3 (64 kbps)", callback_data=cb_string_64.encode("UTF-8")),
                    InlineKeyboardButton(
                        "🎧 MP3 (128 kbps)", callback_data=cb_string_128.encode("UTF-8"))
                ])
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "🎧 MP3 (320 kbps)", callback_data=cb_string.encode("UTF-8"))
                ])
        else:
            try:
                total_length = await ContentLength(url)
            except Exception as e:
                await info_msg.edit_text(
                    Translation.NO_VOID_FORMAT_FOUND.format(str(e)),
                    disable_web_page_preview=True
                )
                return
            format_id = response_json["format_id"]
            format_ext = response_json["ext"]
            cb_string_file = "{}={}={}={}".format(
                "file", format_id, format_ext, json_name)
            cb_string_video = "{}={}={}={}".format(
                "video", format_id, format_ext, json_name)
            if format_ext in Config.VIDEO_FORMATS:
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "🎥 video " + format_ext + " ~" + total_length,
                        callback_data=(cb_string_video).encode("UTF-8")
                    ),
                    InlineKeyboardButton(
                        "📃 file " + format_ext + " ~" + total_length,
                        callback_data=(cb_string_file).encode("UTF-8")
                    )
                ])
            elif format_ext in Config.AUDIO_FORMATS:
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "🎧 audio " + format_ext + " ~" + total_length,
                        callback_data=(cb_string_video).encode("UTF-8")
                    ),
                    InlineKeyboardButton(
                        "📄 file " + format_ext + " ~" + total_length,
                        callback_data=(cb_string_file).encode("UTF-8")
                    )
                ])
            else:
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "📃 file " + format_ext + " ~" + total_length,
                        callback_data=(cb_string_file).encode("UTF-8")
                    )
                ])
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        await info_msg.edit_text(
            Translation.FORMAT_SELECTION,
            reply_markup=reply_markup
        )
    else:
        # fallback for nonnumeric port a.k.a seedbox.io
        inline_keyboard = []
        cb_string_file = "{}={}={}={}".format(
            "file", "LFO", "NONE", json_name)
        cb_string_video = "{}={}={}={}".format(
            "video", "OFL", "ENON", json_name)
        inline_keyboard.append([
            InlineKeyboardButton(
                "🎥 video*",
                callback_data=(cb_string_video).encode("UTF-8")
            ),
            InlineKeyboardButton(
                "📄 file*",
                callback_data=(cb_string_file).encode("UTF-8")
            )
        ])
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        await info_msg.edit_text(
            Translation.FORMAT_SELECTION,
            reply_markup=reply_markup
        )