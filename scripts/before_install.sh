#!/usr/bin/env bash
set -e

echo "[BeforeInstall] Stop old service & cleaning up..."

# 若使用 systemd 管理 Gunicorn
if systemctl is-active --quiet gunicorn; then
  sudo systemctl stop gunicorn
fi

# 切換至要清理的目錄
cd /home/ec2-user/myproject/TravelProjectDjango

# 刪除除 .env 與 Python-3.10.11 以外的所有檔案/目錄，使用 sudo 以避免 permission denied
ls -A | grep -v -E '^(Python-3\.10\.11|\.env|staticfiles)$' | xargs sudo rm -rf

echo "[BeforeInstall] Done"
