"""Bot configuration loaded from the environment."""
import os


DISCORD_TOKEN = "MTUyMzAyMDkxOTMwMjUyNDkzOA.Gy5qOc.8gqRKp7MSAhSemBxUfk8sW_cr1KN3qHLHIlyqQ"
GUILD_ID = 1045726243473084496
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ALERT_CHANNEL_ID = os.getenv("ALERT_CHANNEL_ID", "")

# LLM (Google Gemini free tier — get a key at https://aistudio.google.com/apikey)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")  # fast + free tier

COMMAND_PREFIX = "!"
