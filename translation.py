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
    HELP_USER = """🤔 How to Use Me? Follow These steps! 👇
    
<b>1. Send URL</b>

If you want a custom caption on your video/file send the name/text you want to set on the video/file in the following format 👇

<b>Link * caption</b> (without extension). 
[Separate the link and the caption name with "*" mark].

<b>Example:</b> https://www.website.com/video.mp4 * caption text

👉 The caption/text you type will be automatically set as the custom name of the uploaded file 😎

<i><b>Note:</b> You can change/add any caption later if you want as explained in the end 🥰</i>

<b>2. Then send Custom Thumbnail when asked while uploading the url</b> (This step is optional) 

🔹 It means it is not necessary to send an image to include as an thumbnail.
If you don't send a thumbnail the video/file will be uploaded with an auto genarated thumbnail from the video.
The thumbnail you send will be used for your next uploads!

Press /delthumbnail if you want to delete the previously saved thumbnail.
(then the video will be uploaded with an auto-genarated thumbnail!)

<b>3. Select the button</b>
  Video-option : Give video/file in video format
  File-option : Give video/file in file format
   
<b>Special feature: 👉 Set caption to any file you want! ✨</b>

🔹 Select an uploaded file/video or forward me <b>Any Telegram File</b> and just write the text you want to be on the file as a reply to the file by selecting it (as replying to a message 😅) and the text you wrote will be attached as caption! 😍

Ex: <a href='https://telegra.ph/file/198bcda5944f787373122.jpg'>Send Like This! It's Easy</a> 🥳

"""
    REPLY_TO_MEDIA_ALBUM_TO_GEN_THUMB = "Reply /generatecustomthumbnail to a media album, to generate custom thumbail."
    ERR_ONLY_TWO_MEDIA_IN_ALBUM = """Media Album should contain only two photos. Please re-send the media album, and then try again, or send only two photos in an album."
You can use /rename command after receiving file to rename it with custom thumbnail support.
"""
    CANCEL_STR = "Process Cancelled."
    ZIP_UPLOADED_STR = "Uploaded {} files in {} seconds."
    SLOW_URL_DECED = "Gosh that seems to be a very slow URL. Since you were screwing my home, I am in no mood to download this file. Meanwhile, why don't you try this:==> https://shrtz.me/PtsVnf6 and get me a fast URL so that I can upload to Telegram, without me slowing down for other users."
