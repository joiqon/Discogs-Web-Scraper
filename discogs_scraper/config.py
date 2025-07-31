import os
from dotenv import load_dotenv

load_dotenv()

DISCOGS_TOKEN = os.getenv('DISCOGS_TOKEN')
OUTPUT_LOCATION = os.getenv('OUTPUT_LOCATION')
