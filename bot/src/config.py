"""Bot configuration loaded from the environment."""
import os

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ALERT_CHANNEL_ID = os.getenv("ALERT_CHANNEL_ID", "")

COMMAND_PREFIX = "!"
LLM_MODEL = "claude-haiku-4-5"  # fast + cheap for short conversational replies
