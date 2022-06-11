class Translation(object):
    START_TEXT = """Hi {} 👋,
💫 I'm Simple Uploader Bot! ✨
You can upload HTTP/HTTPS direct link, Using this bot!

/help for more details!"""
    FORMAT_SELECTION = "<b>If you haven't set <a href='{}'>a thumbnail</a> before you can send a photo now. If you don't want to don't worry - You will get an auto genarated thumbnail from the video to your upload 😎</b>\n\n👇𝗦𝗲𝗹𝗲𝗰𝘁 𝗔𝗻𝗱 𝗖𝗵𝗼𝘀𝗲 𝗬𝗼𝘂𝗿 𝗙𝗼𝗿𝗺𝗮𝘁👇\n(If your link is a video and if you want it as a streamable video select a video option. If you want your upload in document format select a file option)\n\n<b>Don't select other format options if it shows any!</b>"
    SET_CUSTOM_USERNAME_PASSWORD = """If you want to download premium videos, provide in the following format:
URL | filename | username | password"""
    DOWNLOAD_START = "<b>File detected: </b>{}\n\n<b>Downloading to my server now...</b> 📥\n\nPlease wait uploading will start as soon as possible 😎"
    UPLOAD_START = "<b>Uploading to Telegram now...</b> 📤"
    RCHD_TG_API_LIMIT = "Downloaded in {} seconds.\nDetected File Size: {}\nSorry. But, I cannot upload files greater than 2GB due to Telegram API limitations."
    AFTER_SUCCESSFUL_UPLOAD_MSG = "👍 Thanks for using @SimpleUploaderV2Bot."
    AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS = "<b>Downloaded in:</b> {} seconds.\n<b>Uploaded in:</b> {} seconds."
    SAVED_CUSTOM_THUMB_NAIL = "Custom video / file thumbnail saved. This image will be used in the video / file."
    DEL_ETED_CUSTOM_THUMB_NAIL = "✅ Custom thumbnail cleared succesfully."
    CUSTOM_CAPTION_UL_FILE = "{}"
    NO_VOID_FORMAT_FOUND = "ERROR...\n<b>YouTubeDL</b> said: {}"
    HELP_USER = """How to Use Me? Follow These steps!
    
1. Send url (example.domain/File.mp4 | New Filename.mp4).
2. Send Image As Custom Thumbnail (Optional).
3. Select the button.
   SVideo - Give File as video with Screenshots
   DFile  - Give File (video) as file with Screenshots
   Video  - Give File as video without Screenshots
   File   - Give File without Screenshots"""
    REPLY_TO_MEDIA_ALBUM_TO_GEN_THUMB = "Reply /generatecustomthumbnail to a media album, to generate custom thumbail."
    ERR_ONLY_TWO_MEDIA_IN_ALBUM = """Media Album should contain only two photos. Please re-send the media album, and then try again, or send only two photos in an album."
You can use /rename command after receiving file to rename it with custom thumbnail support.
"""
    CANCEL_STR = "Process Cancelled."
    ZIP_UPLOADED_STR = "Uploaded {} files in {} seconds."
    SLOW_URL_DECED = "Gosh that seems to be a very slow URL. Since you were screwing my home, I am in no mood to download this file. Meanwhile, why don't you try this:==> https://shrtz.me/PtsVnf6 and get me a fast URL so that I can upload to Telegram, without me slowing down for other users."
