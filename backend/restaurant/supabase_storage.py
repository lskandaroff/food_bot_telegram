"""
Supabase Storage uchun to'liq Django Storage backend.
Rasmlarni Supabase Bucket ga yuklaydi va public URL beradi.
"""
import os
import uuid
import mimetypes
import logging
import requests
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible

logger = logging.getLogger('restaurant')


@deconstructible
class SupabaseStorage(Storage):
    """
    Rasmlarni Supabase Storage ga yuklaydi.
    Env variables:
      SUPABASE_URL       — masalan: https://xxxx.supabase.co
      SUPABASE_KEY       — anon/public yoki service_role key
      SUPABASE_BUCKET    — bucket nomi (default: food-images)
    """

    def __init__(self, *args, **kwargs):
        raw_url = str(os.environ.get('SUPABASE_URL', '')).strip()
        for bad in ['\r', '\n', '%0a', '%0A', '%0d', '%0D', ' ']:
            raw_url = raw_url.replace(bad, '')
        if '/rest/v1' in raw_url:
            raw_url = raw_url.split('/rest/v1')[0]
        self.supabase_url = raw_url.rstrip('/')

        raw_key = str(os.environ.get('SUPABASE_KEY', '')).strip()
        for bad in ['\r', '\n', '%0a', '%0A', '%0d', '%0D', ' ']:
            raw_key = raw_key.replace(bad, '')
        self.supabase_key = raw_key

        raw_bucket = str(os.environ.get('SUPABASE_BUCKET', 'food-images')).strip()
        for bad in ['\r', '\n', '%0a', '%0A', '%0d', '%0D', ' ']:
            raw_bucket = raw_bucket.replace(bad, '')
        self.bucket = raw_bucket

    def _get_headers(self):
        return {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
        }

    def _upload_url(self, name):
        clean_name = str(name).lstrip('/')
        return f"{self.supabase_url}/storage/v1/object/{self.bucket}/{clean_name}"

    def _public_url(self, name):
        clean_name = str(name).lstrip('/')
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket}/{clean_name}"

    def _open(self, name, mode='rb'):
        """Supabase dan faylni o'qish (Django ImageField ochganda kerak)."""
        url = self.url(name)
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                return ContentFile(resp.content, name=name)
        except Exception as e:
            logger.error(f"Supabase _open error for {name}: {e}")
        raise FileNotFoundError(f"Fayl topilmadi: {name}")

    def _save(self, name, content):
        """Faylni Supabase ga yuklaydi."""
        dir_name, file_name = os.path.split(str(name))
        base_name, ext = os.path.splitext(file_name)
        unique_file = f"{base_name}_{uuid.uuid4().hex[:8]}{ext}"
        
        if dir_name:
            unique_name = f"{dir_name}/{unique_file}".replace('\\', '/')
        else:
            unique_name = unique_file

        content_type, _ = mimetypes.guess_type(name)
        if not content_type:
            content_type = 'image/jpeg'

        headers = self._get_headers()
        headers['Content-Type'] = content_type

        # Content position reset
        if hasattr(content, 'seek'):
            content.seek(0)
        file_data = content.read()

        try:
            resp = requests.post(
                self._upload_url(unique_name),
                headers=headers,
                data=file_data,
                timeout=30
            )

            if resp.status_code not in (200, 201):
                logger.error(f"Supabase upload error ({resp.status_code}): {resp.text}")
                raise Exception(
                    f"Supabase ga yuklashda xato ({resp.status_code}): {resp.text}"
                )
        except Exception as e:
            logger.error(f"Supabase upload exception: {e}")
            raise

        return unique_name

    def url(self, name):
        """Public URL qaytaradi."""
        if not name:
            return ''
        name_str = str(name)
        if name_str.startswith('http'):
            return name_str
        return self._public_url(name_str)

    def exists(self, name):
        """Fayl borligini tekshirish."""
        if not name:
            return False
        name_str = str(name)
        if name_str.startswith('http'):
            return True
        try:
            headers = self._get_headers()
            resp = requests.head(self._upload_url(name_str), headers=headers, timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def delete(self, name):
        """Faylni o'chirish."""
        if not name:
            return
        try:
            headers = self._get_headers()
            url = f"{self.supabase_url}/storage/v1/object/{self.bucket}"
            requests.delete(url, headers=headers, json={"prefixes": [str(name)]}, timeout=10)
        except Exception as e:
            logger.error(f"Supabase delete error: {e}")

    def size(self, name):
        """Fayl hajmini qaytaradi."""
        try:
            headers = self._get_headers()
            resp = requests.head(self._upload_url(name), headers=headers, timeout=5)
            if resp.status_code == 200 and 'Content-Length' in resp.headers:
                return int(resp.headers['Content-Length'])
        except Exception:
            pass
        return 0

    def deconstruct(self):
        return ('restaurant.supabase_storage.SupabaseStorage', [], {})
