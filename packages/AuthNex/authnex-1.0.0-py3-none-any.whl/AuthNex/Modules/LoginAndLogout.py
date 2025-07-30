from pyrogram import filters
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler
import datetime
from AuthNex.Database import user_col, sessions_col
from AuthNex import app

login_state = {}


async def start_login(_, message: Message):
    user_id = message.from_user.id
    login_state[user_id] = {"step": "mail"}
    await message.reply("📧 Please enter your mail to login:")


async def handle_login_input(_, message: Message):
    user_id = message.from_user.id
    if user_id not in login_state:
        return

    state = login_state[user_id]
    text = message.text.strip()

    if state["step"] == "mail":
        state["mail"] = text
        state["step"] = "password"
        await message.reply("🔐 Enter your password:")
    elif state["step"] == "password":
        mail = state["mail"]
        password = text

        # Check user exists
        user = await user_col.find_one({"Mail": mail, "Password": password})
        if not user:
            await message.reply("❌ Invalid mail or password. Try again.")
            del login_state[user_id]
            return

        # Save session
        await sessions_col.insert_one({
            "telegram_id": user_id,
            "mail": mail,
            "login_time": datetime.datetime.utcnow()
        })

        await message.reply(f"✅ Successfully logged in as **{user.get('Name')}**")
        del login_state[user_id]


async def logout(_, message: Message):
    user_id = message.from_user.id
    session = await sessions_col.find_one({"telegram_id": user_id})
    if not session:
        await message.reply("❌ You are not logged in.")
        return
    
    
    await sessions_col.delete_many({"telegram_id": user_id})
    await message.reply("🔓 Logged out successfully!")


async def whoami(_, message: Message):
    user_id = message.from_user.id
    session = await sessions_col.find_one({"telegram_id": user_id})
    if not session:
        await message.reply("❌ You are not logged in.")
        return

    user = await user_col.find_one({"Mail": session["mail"]})
    if not user:
        await message.reply("⚠️ Account not found.")
        return

    await message.reply(
        f"🧾 You are logged in as:\n\n"
        f"**Name:** {user['Name']}\n"
        f"**Mail:** {user['Mail']}\n"
        f"**Age:** {user['Age']}\n"
        f"**Password:** {user['Password']}\n"
        f"**Auth-Coins:** {user['AuthCoins']}"
    )

# Register Handlers
login1 = MessageHandler(start_login, filters.command("login") & filters.private)
login2 = MessageHandler(handle_login_input, filters.private)
logout = MessageHandler(logout, filters.command("logout") & filters.private)
profile = MessageHandler(whoami, filters.command("profile") & filters.private)


app.add_handler(login1)
app.add_handler(login2)
app.add_handler(logout)
app.add_handler(profile)
