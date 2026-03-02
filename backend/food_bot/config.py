import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

TOKEN = os.getenv('BOT_TOKEN', '6593061827:AAFrOGTMJXrYVz5QzoOKZti3uuuQHHGMk64')
API_URL = os.getenv('API_URL', 'http://127.0.0.1:8000')
DELIVERY_PERSON_ID = int(os.getenv('DELIVERY_PERSON_ID', '779171993'))