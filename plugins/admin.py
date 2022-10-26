
from pyrogram import Client
from pyrogram import filters
from config import Config
from database.access import clinton

@Client.on_message(filters.command('total'))
async def stats(bot, message):
    if message.from_user.id != Config.OWNER_ID:
        return 
    total_users = await clinton.total_users_count()
    await message.reply_text(text=f"<b>Total users:</b> {total_users}", quote=True)
