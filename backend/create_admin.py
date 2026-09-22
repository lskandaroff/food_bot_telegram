import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_admin():
    User = get_user_model()
    
    username = os.getenv('ADMIN_USERNAME', 'admin')
    password = os.getenv('ADMIN_PASSWORD', 'admin12345')
    email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, password=password, email=email)
        print(f"[OK] Admin user created: username='{username}'")
    else:
        print(f"[INFO] Admin user '{username}' already exists.")

if __name__ == '__main__':
    create_admin()
