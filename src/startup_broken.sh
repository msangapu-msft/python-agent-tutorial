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

echo "Starting Flask app..."

cd /home/site/wwwroot
gunicorn app:app --bind=0.0.0.0:8000