"""
1. food-images bucket yaratadi (yo'q bo'lsa) va public qiladi
2. media/dishes/ papkasidagi barcha rasmlarni Supabase ga yuklaydi
3. DB dagi image path larni yangilaydi
"""
import os
import sys
import sqlite3
import mimetypes
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '').strip().replace('\r','').replace('\n','').rstrip('/')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '').strip().replace('\r','').replace('\n','')
BUCKET = os.environ.get('SUPABASE_BUCKET', 'food-images').strip().replace('\r','').replace('\n','')

MEDIA_DIR = os.path.join(os.path.dirname(__file__), 'media')
DB_PATH   = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': 'Bearer ' + SUPABASE_KEY,
}

print("=" * 60)
print("SUPABASE MIGRATE TOOL")
print("=" * 60)
print("URL   :", SUPABASE_URL)
print("Bucket:", BUCKET)
print()

# ─────────────────────────────────────────────
# 1. Ulanishni tekshirish
# ─────────────────────────────────────────────
print("[1/4] Supabase ulanishi tekshirilmoqda...")
try:
    r = requests.get(SUPABASE_URL + "/storage/v1/bucket", headers=headers, timeout=10)
    if r.status_code == 200:
        print("      [OK] Ulanish muvaffaqiyatli!")
    else:
        print("      [X] Xato:", r.status_code, r.text[:200])
        sys.exit(1)
except Exception as e:
    print("      [X] Ulanib bo'lmadi:", e)
    sys.exit(1)

# ─────────────────────────────────────────────
# 2. Bucket yaratish / public qilish
# ─────────────────────────────────────────────
print()
print("[2/4] Bucket tekshirilmoqda:", BUCKET)
r = requests.get(SUPABASE_URL + "/storage/v1/bucket/" + BUCKET, headers=headers, timeout=10)

if r.status_code == 404:
    print("      Bucket yo'q — yaratilmoqda...")
    cr = requests.post(
        SUPABASE_URL + "/storage/v1/bucket",
        headers={**headers, 'Content-Type': 'application/json'},
        json={"id": BUCKET, "name": BUCKET, "public": True},
        timeout=10
    )
    if cr.status_code in (200, 201):
        print("      [OK] Bucket yaratildi va PUBLIC qilindi!")
    else:
        print("      [X] Yaratishda xato:", cr.status_code, cr.text)
        sys.exit(1)

elif r.status_code == 200:
    data = r.json()
    if not data.get('public', False):
        print("      Bucket PRIVATE — PUBLIC qilinmoqda...")
        pr = requests.put(
            SUPABASE_URL + "/storage/v1/bucket/" + BUCKET,
            headers={**headers, 'Content-Type': 'application/json'},
            json={"public": True},
            timeout=10
        )
        if pr.status_code in (200, 204):
            print("      [OK] Bucket PUBLIC qilindi!")
        else:
            print("      [X] Public qilishda xato:", pr.status_code, pr.text)
    else:
        print("      [OK] Bucket allaqachon PUBLIC!")
else:
    print("      [X] Bucket tekshirishda xato:", r.status_code, r.text[:200])
    sys.exit(1)

# ─────────────────────────────────────────────
# 3. Rasmlarni yuklash
# ─────────────────────────────────────────────
print()
print("[3/4] Rasmlar yuklanmoqda...")

path_mapping = {}  # eski_path -> yangi_path

def upload_file(local_path, remote_name):
    """Faylni Supabase ga yuklaydi, URL qaytaradi."""
    content_type, _ = mimetypes.guess_type(local_path)
    if not content_type:
        content_type = 'image/jpeg'

    with open(local_path, 'rb') as f:
        data = f.read()

    upload_headers = {**headers, 'Content-Type': content_type}
    url = SUPABASE_URL + "/storage/v1/object/" + BUCKET + "/" + remote_name

    # Avval DELETE qilib, keyin POST (upsert)
    requests.delete(url, headers=headers, timeout=5)

    r = requests.post(url, headers=upload_headers, data=data, timeout=30)
    if r.status_code in (200, 201):
        public_url = SUPABASE_URL + "/storage/v1/object/public/" + BUCKET + "/" + remote_name
        return public_url
    else:
        print("      [X] Yuklashda xato:", r.status_code, r.text[:100])
        return None

# media/ papkasidagi barcha papkalar
uploaded = 0
failed = 0
for folder in ['dishes', 'menus', 'menu_images']:
    folder_path = os.path.join(MEDIA_DIR, folder)
    if not os.path.exists(folder_path):
        continue
    for filename in os.listdir(folder_path):
        local_path = os.path.join(folder_path, filename)
        if not os.path.isfile(local_path):
            continue
        
        # Kengaytmani tekshirish
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']:
            continue

        remote_name = folder + "/" + filename
        # Kirill harflarni URL encode qilamiz
        print("      Yuklanmoqda:", remote_name, end=" ... ")
        
        url = upload_file(local_path, remote_name)
        if url:
            print("[OK]")
            path_mapping[folder + "/" + filename] = remote_name
            path_mapping[folder + "\\" + filename] = remote_name
            uploaded += 1
        else:
            print("[X]")
            failed += 1

print()
print("      Yuklandi:", uploaded, "ta | Xato:", failed, "ta")

# ─────────────────────────────────────────────
# 4. DB ni yangilash
# ─────────────────────────────────────────────
print()
print("[4/4] Database yangilanmoqda...")
try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title, image FROM restaurant_dish")
    dishes = cur.fetchall()
    
    updated = 0
    for dish_id, title, old_image in dishes:
        if not old_image:
            continue
        
        # Normalize path
        norm = old_image.replace('\\', '/')
        
        # path_mapping da bor bo'lsa yangilaymiz
        if norm in path_mapping:
            new_path = path_mapping[norm]
            cur.execute("UPDATE restaurant_dish SET image = ? WHERE id = ?", (new_path, dish_id))
            print("      [OK]", title, "->", new_path)
            updated += 1
        else:
            # Fayl local da bormi tekshirish
            local_check = os.path.join(MEDIA_DIR, norm)
            if os.path.exists(local_check):
                # Yuklash kerak edi, lekin mapping da yo'q — kengashtma muammo bo'lishi mumkin
                print("      [!] Topilmadi mapping da:", title, "|", norm)
            else:
                print("      [-] Skip (local fayl yo'q):", title, "|", norm)
    
    conn.commit()
    conn.close()
    print()
    print("      DB yangilandi:", updated, "ta taom")

except Exception as e:
    print("      [X] DB xato:", e)

print()
print("=" * 60)
print("TUGADI!")
print("Endi rasmlarni tekshiring:")
print("  python check_supabase.py")
print("=" * 60)
