from pyrogram import Client, filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from AuthNex import app
from AuthNex.Database import user_col, sessions_col
import random
import asyncio
from pyrogram.handlers import MessageHandler
import datetime


user_states = {}

# Step 1: Start Account Creation
async def create_account(_, message: Message):
    user_id = message.from_user.id
    if await sessions_col.find_one({"_id": user_id}):
        await message.reply("🥲") 
        await message.reply("𝗦𝗼𝗿𝗿𝘆 𝗯𝘂𝘁 𝘆𝗼𝘂 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗵𝗮𝘃𝗲 𝗮 𝗮𝗰𝗰𝗼𝘂𝗻𝘁 𝘄𝗶𝘁𝗵 𝗮 𝗻𝗮𝗺𝗲.")
        return 
    user_states[user_id] = {"step": "name", "user_id": user_id}
    await message.reply("[ℍ𝗢𝕊𝗧] ==> 𝗣𝗹𝗲𝗮𝘀𝗲 𝗲𝗻𝘁𝗲𝗿 𝘆𝗼𝘂𝗿 𝗻𝗮𝗺𝗲 𝗳𝗶𝗿𝘀𝘁.")

# Step 2–6: Handle Input Steps
async def handle_register_step(_, message: Message):
    user_id = message.from_user.id
    if user_id not in user_states:
        return

    state = user_states[user_id]
    text = message.text.strip()

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

    # Step: NAME
    if state["step"] == "name":
        if await user_col.find_one({"Name": message.text}):
            await message.reply("😔")
            await message.reply("𝚂𝚘𝚛𝚛𝚢 𝚋𝚞𝚝 𝚝𝚑𝚎 𝙽𝚊𝚖𝚎 𝚒𝚜 𝙰𝚕𝚛𝚎𝚊𝚍𝚢 𝚝𝚊𝚔𝚎𝚗 𝚋𝚢 𝚜𝚘𝚖𝚎𝚘𝚗𝚎") 
            return 

        if len(text) < 2:
            return await message.reply("⚠️ Name should be at least 2 characters.")
        state["name"] = text
        state["step"] = "age"
        return await message.reply("[ℍ𝗢𝕊𝗧] ==> 𝗣𝗹𝗲𝗮𝘀𝗲 𝗲𝗻𝘁𝗲𝗿 𝘆𝗼𝘂𝗿 𝗮𝗴𝗲 𝗻𝗼𝘄")

    # Step: AGE
    elif state["step"] == "age":
        if not text.isdigit() or not (13 <= int(text) <= 100):
            return await message.reply("⚠️ Enter a valid age between 13 and 100.")
        state["age"] = int(text)
        state["step"] = "mail"
        return await message.reply("[ℍ𝗢𝕊𝗧] ==> 𝗡𝗼𝘄 𝗰𝗿𝗲𝗮𝘁𝗲 𝘆𝗼𝘂𝗿 𝗼𝘄𝗻 [𝔸𝗨𝗧𝗛ℕ𝗘𝗫] 𝗺𝗮𝗶𝗹.\n𝗜𝗡𝗦𝗨𝗥𝗘 𝗶𝘁 𝗲𝗻𝗱𝘀 𝘄𝗶𝘁𝗵 @AuthNex.Codes")

    # Step: MAIL
    elif state["step"] == "mail":
        if not text.endswith("@AuthNex.Codes") or " " in text:
            return await message.reply("⚠️ Mail must end with @AuthNex.Codes and have no spaces.")
        if await user_col.find_one({"Mail": message.text}):
            await message.reply("💔 𝚂𝚘𝚛𝚛𝚢 𝚃𝚑𝚎 𝙼𝚊𝚒𝚕 𝙸𝚜 𝙰𝚕𝚛𝚎𝚊𝚍𝚢 𝚃𝚊𝚔𝚎𝚗 𝚋𝚢 𝚜𝚘𝚖𝚎 𝚘𝚗𝚎 𝚎𝚕𝚜𝚎") 
        state["mail"] = text
        state["step"] = "password"
        return await message.reply("[ℍ𝗢𝕊𝗧] ==> 𝗡𝗼𝘄 𝗰𝗿𝗲𝗮𝘁𝗲 𝗮 𝘀𝘁𝗿𝗼𝗻𝗴 𝗽𝗮𝘀𝘀𝘄𝗼𝗿𝗱 (𝗮𝘁 𝗹𝗲𝗮𝘀𝘁 𝟲 𝗰𝗵𝗮𝗿𝘀)")

    # Step: PASSWORD
    elif state["step"] == "password":
        if len(text) < 6:
            return await message.reply("⚠️ Password must be at least 6 characters.")
        state["password"] = text
        state["step"] = "username"
        return await message.reply("[ℍ𝗢𝕊𝗧] ==> 𝗠𝗮𝗸𝗲 𝗮 𝘂𝗻𝗶𝗾𝘂𝗲 𝗨𝘀𝗲𝗿𝗡𝗮𝗺𝗲 𝘀𝘁𝗮𝗿𝘁𝗶𝗻𝗴 𝘄𝗶𝘁𝗵 `$`")

    # Step: USERNAME
    elif state["step"] == "username":
        if not text.startswith("$") or " " in text:
            return await message.reply("⚠️ Username must start with `$` and contain no spaces.")
        er = await user_col.find_one({"username": text})
        if er:
            return await message.reply("⚠️ Username already exists, try another.")
        state["username"] = text 
        
        
         
        m = await message.reply_text(f"𝙲𝚛𝚎𝚊𝚝𝚎 𝙰𝚌𝚌𝚘𝚞𝚗𝚝 𝚏𝚘𝚛 {state['name']}🌟\n{bars[10]}", parse_mode=ParseMode.MARKDOWN) 
        for bar in bars:
            await m.edit_text(f"𝙲𝚛𝚎𝚊𝚝𝚎 𝙰𝚌𝚌𝚘𝚞𝚗𝚝 𝚏𝚘𝚛 {state['name']}🌟\n{bar}", parse_mode=ParseMode.MARKDOWN) 
            await asyncio.sleep(1) 

        await m.edit_text(f"""✨ 𝘾𝙧𝙚𝙖𝙩𝙚𝙙 𝘼𝙘𝙘𝙤𝙪𝙣𝙩 𝙤𝙛 𝔸𝗨𝗧𝗛ℕ𝗘𝕏 𝙛𝙤𝙧 {state['name']}\n{bar[10]}\n𝘿𝙤 /profile 𝙩𝙤 𝙨𝙚𝙚 𝙮𝙤𝙪𝙧  𝔸𝗨𝗧𝗛ℕ𝗘𝕏 𝙋𝙧𝙤𝙛𝙞𝙡𝙚.💘\n\n
╔══╦╗════╔╗═╔╗╔╗
╚╗╔╣╚╦═╦═╣╚╗║╚╝╠═╦╦╗
═║║║║║╬║║║╩║╚╗╔╣║║║║
═╚╝╚╩╩╩╩╩╩╩╝═╚╝╚═╩═╝
╯ """) 
        await user_col.insert_one({"Name": state['name'], 
                                   "Age": state['age'], 
                                   "Mail": state['mail'], 
                                   "Password": state['password'], 
                                   "UserName": state['username'],
                                   "AuthCoins": 0,
                                   "Msgs": 0,
                                  })
        await sessions_col.insert_one({"_id": user_id,
                                      "mail": state["mail"],
                                      "login": datetime.now()
                                     }) 
        del user_states[user_id]
        
# Handlers
acc_start = MessageHandler(create_account, filters.command("Create_Acc") & filters.private)
acc_steps = MessageHandler(handle_register_step, filters.private)





