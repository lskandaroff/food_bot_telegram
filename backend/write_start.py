import os

filepath = os.path.join('backend', 'start.sh')
content = "#!/bin/bash\n\n# Start Telegram bot in background\n(cd food_bot && python main.py >> /tmp/bot.log 2>&1) &\n\n# Start Django with gunicorn\nexec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-10000} --workers 2 --timeout 120\n"

with open(filepath, 'w', newline='\n') as f:
    f.write(content)

print(f"Written {len(content)} bytes with LF line endings to {filepath}")
