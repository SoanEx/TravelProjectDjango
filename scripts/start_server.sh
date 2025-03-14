#!/usr/bin/env bash
set -e

echo "[ApplicationStart] Starting (or Restarting) Gunicorn via systemd..."

# 若你已在 /etc/systemd/system/gunicorn.service
# 設 WorkingDirectory=/home/ec2-user/myproject/TravelProjectDjango/travelProject
# 和 ExecStart=...gunicorn --bind 127.0.0.1:8000 travelProject.wsgi:application
# 這裡只要重啟服務即可：

sudo systemctl daemon-reload  # 確保最新服務檔
sudo systemctl restart gunicorn
sudo systemctl enable gunicorn  # (可選) 開機自動啟動

sudo chown -R ec2-user:ec2-user /home/ec2-user/myproject/TravelProjectDjango/travelProject/staticfiles
sudo chmod -R 755 /home/ec2-user/myproject/TravelProjectDjango/travelProject/staticfiles


echo "[ApplicationStart] Done"
