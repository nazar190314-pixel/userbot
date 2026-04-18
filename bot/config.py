import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
SESSION_NAME = os.getenv("SESSION_NAME", "venombot")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")