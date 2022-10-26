
from pyrogram import filters
from pyrogram import Client
from plugins.youtube_dl_button import youtube_dl_call_back
from plugins.dl_button import ddl_call_back
from . import fembed

@Client.on_callback_query(filters.regex('^X0$'))
async def delt(bot, message):
    await message.message.delete(True)

@Client.on_callback_query()
async def button(bot, message):
    cb_data = message.data
    if "|" in cb_data:
        if "fembed" in cb_data.split("|")[0]:
            await fembed.download(bot, message)
        else:
            await youtube_dl_call_back(bot, message)
    elif "=" in cb_data:
        await ddl_call_back(bot, message)