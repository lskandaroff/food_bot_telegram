#!/bin/bash

# Start Telegram bot in a subshell (background)
(cd food_bot && python main.py) &

# Start Django with gunicorn on Render's PORT (default 10000)
gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-10000}
