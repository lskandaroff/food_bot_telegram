"""
food-images bucket ni PUBLIC qiladi.
Supabase project tiklanganidan keyin ishlatish.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '').strip().replace('\r','').replace('\n','').rstrip('/')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '').strip().replace('\r','').replace('\n','')
BUCKET = os.environ.get('SUPABASE_BUCKET', 'food-images').strip().replace('\r','').replace('\n','')

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': 'Bearer ' + SUPABASE_KEY,
    'Content-Type': 'application/json',
}

print("Bucket tekshirilmoqda:", BUCKET)

# Bucket holatini olish
resp = requests.get(
    SUPABASE_URL + "/storage/v1/bucket/" + BUCKET,
    headers=headers,
    timeout=10
)

if resp.status_code == 200:
    data = resp.json()
    is_public = data.get('public', False)
    print("Hozirgi holat - PUBLIC:", is_public)

    if not is_public:
        print("Bucket ni PUBLIC qilish...")
        patch_resp = requests.put(
            SUPABASE_URL + "/storage/v1/bucket/" + BUCKET,
            headers=headers,
            json={"public": True},
            timeout=10
        )
        if patch_resp.status_code in (200, 204):
            print("[OK] Bucket muvaffaqiyatli PUBLIC qilindi!")
        else:
            print("[X] Xato:", patch_resp.status_code, patch_resp.text)
    else:
        print("[OK] Bucket allaqachon PUBLIC!")

elif resp.status_code == 404:
    print("[!] Bucket topilmadi. Yangi bucket yaratilmoqda...")
    create_resp = requests.post(
        SUPABASE_URL + "/storage/v1/bucket",
        headers=headers,
        json={"id": BUCKET, "name": BUCKET, "public": True},
        timeout=10
    )
    if create_resp.status_code in (200, 201):
        print("[OK] Bucket yaratildi va PUBLIC qilindi:", BUCKET)
    else:
        print("[X] Yaratishda xato:", create_resp.status_code, create_resp.text)

else:
    print("[X] Ulanishda xato:", resp.status_code)
    print("Javob:", resp.text[:300])
    print()
    print("Ehtimol Supabase project paused (to'xtatilgan).")
    print("Dashboard: https://supabase.com/dashboard/project/ihechhbcvsnhsqpogpxb")
    print("'Restore project' tugmasini bosing, keyin bu scriptni qayta ishgating.")
