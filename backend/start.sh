#!/bin/bash

# Start Telegram bot in a subshell (background)
(cd food_bot && python main.py) &

# Start Django with gunicorn (stays in backend root)
gunicorn config.wsgi:application
