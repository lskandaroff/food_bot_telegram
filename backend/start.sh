#!/bin/bash

# Database migratsiyasini bajarish
python manage.py migrate --noinput

# Statik fayllarni yig'ish (Whitenoise uchun)
python manage.py collectstatic --noinput

# Telegram botni fonda ishga tushirish
(cd food_bot && python main.py >> /tmp/bot.log 2>&1) &

# Django Web App serverini ishga tushirish (Northflank bergan PORT yoki 8000)
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120
