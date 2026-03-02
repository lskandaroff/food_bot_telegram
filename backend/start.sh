#!/bin/bash

# Start Telegram bot in background
(cd food_bot && python main.py >> /tmp/bot.log 2>&1) &

# Start Django with gunicorn
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-10000} --workers 2 --timeout 120
