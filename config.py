import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8806756704:AAFIeU6oR6NfdCi9S2n_21WQiXN7ew8b44A")
OWNER_ID = int(os.getenv("OWNER_ID", "8230452118"))

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://tgjiro441_db_user:Tgjirosamkun@cluster0.9reqco1.mongodb.net/?appName=Cluster0")
DB_NAME = os.getenv("DB_NAME", "filesharebot")

# Telegram Storage Channel
STORAGE_CHANNEL = int(os.getenv("STORAGE_CHANNEL", "-1004387179286"))  # Private channel ID

# Bot Settings
BOT_USERNAME = os.getenv("BOT_USERNAME", "Propross_bot")
START_IMAGE = os.getenv("START_IMAGE", "https://graph.org/file/fdc4357abfaba23255e98-24d1bbfa3888cdfcfe.jpg")  # Optional start image URL or file_id

# Link Base
LINK_BASE = f"https://t.me/{BOT_USERNAME}?start="
