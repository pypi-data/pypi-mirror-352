from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
import asyncio
from pyrogram.handlers import MessageHandler
from config import SUDO
from AuthNex import app as AuthNex
from AuthNex.Database import user_col, sessions_col

# Reset command function
async def reset_handler(_, m: Message):
    bars = [
        "▱▱▱▱▱▱▱▱▱▱  0%",
        "▰▱▱▱▱▱▱▱▱▱ 10%",
        "▰▰▱▱▱▱▱▱▱▱ 20%",
        "▰▰▰▱▱▱▱▱▱▱ 30%",
        "▰▰▰▰▱▱▱▱▱▱ 40%",
        "▰▰▰▰▰▱▱▱▱▱ 50%",
        "▰▰▰▰▰▰▱▱▱▱ 60%",
        "▰▰▰▰▰▰▰▱▱▱ 70%",
        "▰▰▰▰▰▰▰▰▱▱ 80%",
        "▰▰▰▰▰▰▰▰▰▱ 90%",
        "▰▰▰▰▰▰▰▰▰▰ 100%"
    ]

    count = await user_col.count_documents({})
    if count == 0:
        msg = await m.reply_text("🧐") 
        await asyncio.sleep(1) 
        await msg.delete()
        await m.reply_text("😕 𝙽𝚘 𝚕𝚘𝚐𝚒𝚗𝚜 𝚏𝚘𝚞𝚗𝚍 𝚒𝚗 𝚏𝚒𝚕𝚎𝚜 📁")
        return

    msg = await m.reply("🧐") 
    await asyncio.sleep(1) 
    await msg.delete() 
    sync = await m.reply("Deleting...")

    for bar in bars:
        await sync.edit_text(f"```shell\n𝔻𝔼𝕃𝔼𝕋𝕀ℕ𝔾...\n{bar}```", parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(0.5)

    await user_col.delete_many({})
    await sessions_col.delete_many({}) # Use delete_many instead of delete (delete is deprecated)

    await sync.edit_text(
        f"𝔸𝕝𝕝 𝔻𝕠𝕟𝕖. 𝔸𝕝𝕝 𝔻𝕒𝕥𝕒 𝕗𝕚𝕝𝕖𝕤 𝕒𝕣𝕖 𝕕𝕖𝕝𝕖𝕥𝕖𝕕.\n{bars[-1]}"
    )

# Proper handler (with correct filters)
ResetHandlerObject = MessageHandler(
    reset_handler,
    filters.command("reset") & (filters.private | filters.group) & filters.user(SUDO)
)

# Register the handler
AuthNex.add_handler(ResetHandlerObject)
