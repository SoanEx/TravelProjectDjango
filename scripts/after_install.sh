#!/usr/bin/env bash
set -e

echo "[AfterInstall] Installing requirements & migrations..."

# 1) 進入 manage.py 所在目錄
cd /home/ec2-user/myproject/TravelProjectDjango/travelProject

# 2) 啟用新的 /home/ec2-user/myproject/venv
source /home/ec2-user/myproject/venv/bin/activate

# 3) 安裝 requirements (注意: ../requirements.txt)
pip install -r ../requirements.txt

# 4) 執行 migrate、collectstatic
python manage.py migrate
python manage.py collectstatic --noinput

echo "[AfterInstall] Done"
