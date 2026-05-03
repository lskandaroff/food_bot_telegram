import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

TOKEN = os.getenv('BOT_TOKEN', '6593061827:AAFrOGTMJXrYVz5QzoOKZti3uuuQHHGMk64')
API_URL = os.getenv('API_URL', 'http://127.0.0.1:8000')
LOCAL_API_URL = 'http://127.0.0.1:8000'

# Render.com automatic URL detection
RENDER_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_HOSTNAME and (API_URL == 'http://127.0.0.1:8000' or API_URL == 'http://localhost:8000'):
    API_URL = f"https://{RENDER_HOSTNAME}"
    LOCAL_API_URL = API_URL  # Renderda ulanish uchun muammo yo'q

DELIVERY_PERSON_ID = int(os.getenv('DELIVERY_PERSON_ID', '779171993'))