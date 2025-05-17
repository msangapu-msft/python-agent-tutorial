#!/bin/bash
set -e
{
  echo "=== Installing dependencies ==="
  python3 -m pip install --upgrade pip
  python3 -m pip install -r /home/site/wwwroot/requirements.txt
  echo "=== Starting app ==="
  python3 -m gunicorn --bind=0.0.0.0:8000 app:app
} 2>&1 | tee /home/site/wwwroot/startup.log