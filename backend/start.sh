#!/bin/bash

# Start Telegram bot in the background
cd food_bot && python main.py &

# Go back to backend root
cd ..

# Start Django with gunicorn
gunicorn config.wsgi:application
