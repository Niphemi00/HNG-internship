from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

print(os.getenv("IP2LOCATION_API_KEY"))
print(os.getenv('OPENWEATHER_API_KEY'))