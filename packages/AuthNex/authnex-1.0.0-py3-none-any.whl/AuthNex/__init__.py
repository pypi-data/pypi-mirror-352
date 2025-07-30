from pyrogram import Client 
from config import *

app = Client("AuthNexLogins",
                 api_id=API_ID, 
                 api_hash=API_HASH, 
                 bot_token=BOT_TOKEN, 
                 plugins=dict(root="AuthNex/Modules") 
                ) 

import logging

logging.basicConfig(
  format="[KuroAI-Beta] %(name)s - %(levelname)s - %(message)s",
  handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
  level=logging.INFO,
)

logger = logging.getLogger(__name__)                            
