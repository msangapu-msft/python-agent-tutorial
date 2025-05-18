#!/bin/bash
echo "Injecting memory bug into app.py..."

# Append memory exhaustion code to the convert_selected() function
sed -i '/def convert_selected():/a\
    # Memory exhaustion block (injected by startup_broken.sh)\n\
    try:\n\
        big_list = []\n\
        for _ in range(10**7):\n\
            big_list.append("X" * 1024)\n\
    except MemoryError:\n\
        from flask import jsonify\n\
        exit(jsonify({"error": "MemoryError occurred"}))\n' /home/site/wwwroot/app.py

set -e
{
  echo "=== Installing dependencies ==="
  python3 -m pip install --upgrade pip
  python3 -m pip install -r /home/site/wwwroot/requirements.txt
  echo "=== Starting app ==="
  python3 -m gunicorn --bind=0.0.0.0:8000 app:app
} 2>&1 | tee /home/site/wwwroot/startup.log