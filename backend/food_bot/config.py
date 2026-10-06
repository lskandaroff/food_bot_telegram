import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

TOKEN = os.getenv('BOT_TOKEN', '8958059129:AAEf0drKmEZioGG8X7v7VTIrRBKkJ-SR3gQ')
API_URL = os.getenv('API_URL', 'http://127.0.0.1:8000')
LOCAL_API_URL = 'http://127.0.0.1:8000'

# Render.com automatic URL detection
RENDER_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_HOSTNAME and (API_URL == 'http://127.0.0.1:8000' or API_URL == 'http://localhost:8000'):
    API_URL = f"https://{RENDER_HOSTNAME}"
    LOCAL_API_URL = API_URL  # Renderda ulanish uchun muammo yo'q

DELIVERY_PERSON_ID = int(os.getenv('DELIVERY_PERSON_ID', '779171993'))

def _parse_admin_ids():
    raw_ids = os.getenv('ADMIN_IDS') or os.getenv('ADMIN_ID') or os.getenv('DELIVERY_PERSON_ID') or '6261098836,779171993'
    ids = []
    for item in str(raw_ids).split(','):
        item = item.strip()
        if item.isdigit():
            ids.append(int(item))
    return ids if ids else [6261098836, 779171993]

ADMIN_IDS = _parse_admin_ids()
ADMIN_ID = ADMIN_IDS[0]
