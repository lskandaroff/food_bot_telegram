"""
Supabase bucket holatini tekshiradi va rasmlarni sinab koradi.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '').strip()
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '').strip()
BUCKET = os.environ.get('SUPABASE_BUCKET', 'food-images').strip()

for bad in ['\r', '\n', ' ']:
    SUPABASE_URL = SUPABASE_URL.replace(bad, '')
    SUPABASE_KEY = SUPABASE_KEY.replace(bad, '')
    BUCKET = BUCKET.replace(bad, '')

SUPABASE_URL = SUPABASE_URL.rstrip('/')

print("=" * 60)
print("SUPABASE TEKSHIRUV")
print("=" * 60)
print("URL:", SUPABASE_URL)
print("Bucket:", BUCKET)
print("Key (boshlang'ich):", SUPABASE_KEY[:30], "...")
print()

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': 'Bearer ' + SUPABASE_KEY,
}

# 1. Bucket holatini tekshirish
print("1. Bucket holatini tekshirish...")
try:
    resp = requests.get(
        SUPABASE_URL + "/storage/v1/bucket/" + BUCKET,
        headers=headers,
        timeout=10
    )
    if resp.status_code == 200:
        data = resp.json()
        is_public = data.get('public', False)
        print("   [OK] Bucket topildi:", BUCKET)
        if is_public:
            print("   [PUBLIC] = YES (bucket public!)")
        else:
            print("   [PUBLIC] = NO - PRIVATE (MUAMMO SHU!)")
            print()
            print("   YECHIM: Supabase Dashboard > Storage > food-images")
            print("           > Edit bucket > 'Public bucket' ni yoqing")
    elif resp.status_code == 401:
        print("   [X] 401 - Key noto'g'ri yoki ruxsat yo'q")
    elif resp.status_code == 404:
        print("   [X] 404 - Bucket topilmadi:", BUCKET)
    else:
        print("   [?] Status:", resp.status_code)
        print("   Response:", resp.text[:200])
except Exception as e:
    print("   [X] Xato:", str(e))

print()

# 2. Bucket ichidagi fayllarni ko'rish
print("2. Bucket ichidagi fayllar...")
try:
    resp = requests.post(
        SUPABASE_URL + "/storage/v1/object/list/" + BUCKET,
        headers={**headers, 'Content-Type': 'application/json'},
        json={"prefix": "", "limit": 5},
        timeout=10
    )
    if resp.status_code == 200:
        files = resp.json()
        if files:
            print("   [OK]", len(files), "ta fayl topildi:")
            for f in files[:5]:
                name = f.get('name', 'unknown')
                print("   -->", name)
                public_url = SUPABASE_URL + "/storage/v1/object/public/" + BUCKET + "/" + name
                try:
                    r = requests.head(public_url, timeout=5)
                    if r.status_code == 200:
                        print("      [OK] Public URL ishlaydi:", public_url)
                    elif r.status_code == 400:
                        print("      [X] 400 - Bucket PRIVATE! Rasm ko'rinmaydi")
                    else:
                        print("      [!] Status:", r.status_code)
                except Exception as ue:
                    print("      [X] URL xato:", str(ue))
        else:
            print("   [!] Bucket bo'sh")
    else:
        print("   [X] Xato:", resp.status_code, resp.text[:200])
except Exception as e:
    print("   [X] Xato:", str(e))

print()
print("=" * 60)
project_id = SUPABASE_URL.split("//")[1].split(".")[0] if "//" in SUPABASE_URL else "unknown"
print("Dashboard: https://supabase.com/dashboard/project/" + project_id + "/storage/buckets")
print("=" * 60)
