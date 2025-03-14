#!/usr/bin/env bash
set -e

echo "[ApplicationStart] Starting service..."

sudo systemctl start gunicorn
sudo systemctl enable gunicorn  # 若想讓它開機自動啟動

echo "[ApplicationStart] Done"
