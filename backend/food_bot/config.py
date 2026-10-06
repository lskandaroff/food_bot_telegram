# Config module for food_bot (v2.0 - Multi-admin support)
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

TOKEN = os.getenv('BOT_TOKEN', '8905877735:AAH8R9FhkCcdKCNkUkD45jLbpjjvfeEvM2Q')
API_URL = os.getenv('API_URL', 'http://127.0.0.1:8000')
LOCAL_API_URL = 'http://127.0.0.1:8000'

# Render.com automatic URL detection
RENDER_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_HOSTNAME and (API_URL == 'http://127.0.0.1:8000' or API_URL == 'http://localhost:8000'):
    API_URL = f"https://{RENDER_HOSTNAME}"
    LOCAL_API_URL = API_URL  # Renderda ulanish uchun muammo yo'q

def _parse_ids(env_name, default_str='6261098836,779171993'):
    raw_val = os.getenv(env_name) or default_str
    ids = []
    for item in str(raw_val).split(','):
        item = item.strip()
        if item.isdigit():
            ids.append(int(item))
    return ids if ids else [6261098836, 779171993]

DELIVERY_PERSON_IDS = _parse_ids('DELIVERY_PERSON_ID', '6261098836,779171993')
DELIVERY_PERSON_ID = DELIVERY_PERSON_IDS[0]

ADMIN_IDS = _parse_ids('ADMIN_IDS', '6261098836,779171993')
ADMIN_ID = ADMIN_IDS[0]


