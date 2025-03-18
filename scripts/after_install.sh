#!/usr/bin/env bash
set -e

echo "[AfterInstall] Installing requirements & migrations..."

# 1) 進入 manage.py 所在目錄
cd /home/ec2-user/myproject/TravelProjectDjango/travelProject

# 2) 啟用 venv（虛擬環境）
source /home/ec2-user/myproject/venv/bin/activate

# 3) 安裝 requirements
pip install -r ../requirements.txt

# 3.5) (選擇性) 調整資料夾權限，確保 collectstatic 時能成功寫入
sudo chown -R ec2-user:ec2-user /home/ec2-user/myproject/TravelProjectDjango/travelProject/staticfiles
sudo chmod -R 755 /home/ec2-user/myproject/TravelProjectDjango/travelProject/staticfiles

# 4) 執行 migrate、collectstatic
python manage.py migrate
python manage.py collectstatic --noinput

echo "[AfterInstall] Done"
