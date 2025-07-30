from motor.motor_asyncio import AsyncIOMotorClient 

MONGO_URI = "mongodb+srv://sufyan532011:2011@authnex.nvjbscr.mongodb.net/?retryWrites=true&w=majority&appName=AuthNex"
Database = AsyncIOMotorClient(MONGO_URI)
AuthNex = Database["AuthNex"]
user_col = AuthNex["USER_LOGINS"]
ban_col = AuthNex["BANNED_USERS"]
sessions_col = AuthNex["SESSIONS"]
