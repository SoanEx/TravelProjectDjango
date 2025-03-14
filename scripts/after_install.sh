#!/usr/bin/env bash
set -e

echo "[AfterInstall] Installing requirements & migrations..."

cd /home/ec2-user/myproject/TravelProjectDjango

# 如果你要使用 Python-3.10.11 或已事先裝好的 venv，可視情況調整
# source Python-3.10.11/venv/bin/activate
# pip install -r requirements.txt

# python manage.py migrate
# python manage.py collectstatic --noinput

echo "[AfterInstall] Done"
