"""
Supabase Storage uchun custom Django storage backend.
Rasmlarni Supabase bucket ga yuklaydi, public URL qaytaradi.
"""
import os
import uuid
import mimetypes
import requests
from django.core.files.storage import Storage
from django.conf import settings
from urllib.parse import urljoin


class SupabaseStorage(Storage):
    """
    Rasmlarni Supabase Storage ga yuklaydi.
    Env variables talab qilinadi:
      SUPABASE_URL       — masalan: https://xxxx.supabase.co
      SUPABASE_KEY       — anon/public yoki service_role key
      SUPABASE_BUCKET    — bucket nomi (default: food-images)
    """

    def __init__(self):
        self.supabase_url = os.environ.get('SUPABASE_URL', '').rstrip('/')
        self.supabase_key = os.environ.get('SUPABASE_KEY', '')
        self.bucket = os.environ.get('SUPABASE_BUCKET', 'food-images')

    def _get_headers(self):
        return {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
        }

    def _upload_url(self, name):
        return f"{self.supabase_url}/storage/v1/object/{self.bucket}/{name}"

    def _public_url(self, name):
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket}/{name}"

    def _save(self, name, content):
        """Faylni Supabase ga yuklaydi, unique nom beradi."""
        ext = os.path.splitext(name)[1]
        unique_name = f"{os.path.splitext(name)[0]}_{uuid.uuid4().hex[:8]}{ext}"

        content_type, _ = mimetypes.guess_type(name)
        if not content_type:
            content_type = 'application/octet-stream'

        headers = self._get_headers()
        headers['Content-Type'] = content_type

        file_data = content.read()

        resp = requests.post(
            self._upload_url(unique_name),
            headers=headers,
            data=file_data,
            timeout=30
        )

        if resp.status_code not in (200, 201):
            raise Exception(
                f"Supabase ga yuklashda xato: {resp.status_code} — {resp.text}"
            )

        return unique_name

    def url(self, name):
        """Public URL qaytaradi."""
        if not name:
            return ''
        # Agar allaqachon to'liq URL bo'lsa, o'zgartirmaymiz
        if name.startswith('http'):
            return name
        return self._public_url(name)

    def exists(self, name):
        """Supabase da fayl borligini tekshirish."""
        headers = self._get_headers()
        resp = requests.head(self._upload_url(name), headers=headers, timeout=10)
        return resp.status_code == 200

    def delete(self, name):
        """Supabase dan faylni o'chirish."""
        headers = self._get_headers()
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket}"
        requests.delete(url, headers=headers, json={"prefixes": [name]}, timeout=10)

    def size(self, name):
        return 0

    def get_accessed_time(self, name):
        raise NotImplementedError

    def get_created_time(self, name):
        raise NotImplementedError

    def get_modified_time(self, name):
        raise NotImplementedError
