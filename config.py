import os
from typing import cast
from dotenv import load_dotenv

load_dotenv()  # Loads .env file

PHEMEX_API_KEY = cast(str, os.getenv("PHEMEX_API_KEY"))
PHEMEX_API_SECRET = cast(str, os.getenv("PHEMEX_API_SECRET"))

if not PHEMEX_API_KEY or not PHEMEX_API_SECRET:
    raise EnvironmentError("Missing Phemex API credentials.")
