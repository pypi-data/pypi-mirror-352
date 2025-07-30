from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler
from pyrogram.enums import ParseMode
from AuthNex import app

LOGS = []
SUDO_USER = [6239769036]

async def logs_handler(_, m: Message):
    if not LOGS:
        await m.reply_text("📭 No error logs yet.")
        return

    logs_text = "```shell\n⚠️ ERROR LOGS:\n\n" + "\n".join(LOGS[-30:]) + "\n```"
    if len(logs_text) > 4096:
        logs_text = "```shell\n⚠️ ERROR LOGS (truncated):\n\n" + "\n".join(LOGS[-25:]) + "\n```"
    await m.reply_text(logs_text, parse_mode=ParseMode.MARKDOWN)

logs = MessageHandler(logs_handler, filters.command("logs") & filters.user(SUDO_USER))
