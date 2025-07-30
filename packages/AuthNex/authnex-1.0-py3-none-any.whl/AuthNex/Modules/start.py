from pyrogram import Client, filters 
from AuthNex import app 
from pyrogram.types import Message 
from pyrogram.handlers import MessageHandler 


async def start_commands(_, message: Message):
  await message.reply_photo(photo="https://files.catbox.moe/vw9cip.jpg",caption="""|  𝔸𝗨𝗧𝗛ℕ𝗘𝗫  |

We offers the best accounts to play game bots and use workers created by [𝔸𝗨𝗧𝗛ℕ𝗘𝗫].
Enjoy reliable performance (⁠◍⁠•⁠ᴗ⁠•⁠◍⁠)

Owner: @M15T3R_C0D3R
Ceo: @Uzumaki_X_Naruto6

[𝗡𝗢𝗧𝗘] Use /create_acc to create your account. 
""") 

start = MessageHandler(start_commands, filters.command('start') & (filters.private | filters.group)) 
