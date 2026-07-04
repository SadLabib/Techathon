"""Bot configuration loaded from the environment."""
import os

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ALERT_CHANNEL_ID = os.getenv("ALERT_CHANNEL_ID", "")

# LLM (Google Gemini free tier — get a key at https://aistudio.google.com/apikey)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")  # fast + free tier

COMMAND_PREFIX = "!"
