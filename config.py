import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env file

PHEMEX_API_KEY = os.getenv("PHEMEX_API")
PHEMEX_API_SECRET = os.getenv("PHEMEX_SECRET")

if not PHEMEX_API_KEY or not PHEMEX_API_SECRET:
    raise EnvironmentError("Missing Phemex API credentials.")
