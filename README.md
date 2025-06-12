# TravelProjectDjango


[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1.6-green?logo=django)](https://www.djangoproject.com/)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-brightgreen?logo=node.js)](https://nodejs.org/)



本專案是一個使用 **Django** 與 **Aws** 管理後端並自動部署的示範專案，
同時包含 React 前端 (位於 `travelProject/personalpage-frontend`) 與多個 Django app。
倉庫內也附有 AWS CodeDeploy 的腳本，方便部署至 EC2。

## 環境需求

- Python 3.10 以上（建議 3.10.11）
- Node.js 18 以上（如需啟動前端）

## 專案初始化

1. 下載專案並切換到目錄：
   ```bash
   git clone <repo-url>
   cd TravelProjectDjango
   ```
2. 安裝後端依賴：
   使用 `pip install -r requirements.txt`。
   
4. 複製 `.env` 檔並填入必要設定，常見變數如下：
   ```env
   DJANGO_SECRET_KEY = yourkey
   DEBUG = True
   ALLOWED_HOSTS = 127.0.0.1,localhost
   
   DB_NAME = yourkey
   DB_USER = yourkey
   DB_PASSWORD = yourkey
   DB_HOST = yourkey
   DB_PORT = 3306
   
   TWILIO_ACCOUNT_SID = yourkey
   TWILIO_AUTH_TOKEN = yourkey
   TWILIO_PHONE_NUMBER = yourkey
   
   GOOGLE_CLIENT_ID = yourkey
   GOOGLE_CLIENT_SECRET = yourkey
   
   GOOGLE_MAPS_API_KEY = yourkey
   OPENAI_API_KEY = yourkey
   LINE_CHANNEL_ACCESS_TOKEN = yourkey
   OPENWEATHER_API_KEY = daec25784413bb901befd71125152f5c
   ```


## 啟動開發伺服器

執行下列指令即可開啟本地伺服器：
```bash
travelProject/manage.py runserver
```
預設會在 `http://127.0.0.1:8000/` 提供服務。

若要啟動 React 前端，進入 `travelProject/personalpage-frontend` 後執行：
```bash
npm install
npm start
```



## 部署

專案提供 AWS CodeDeploy 配置 (`appspec.yml`) 及三個部署腳本：
- `scripts/before_install.sh`
- `scripts/after_install.sh`
- `scripts/start_server.sh`

這些腳本會在部署流程中自動安裝依賴、執行遷移並啟動服務，可依需求調整。

## 專案結構

完整的目錄架構可參考 `project_structure.txt`，以下為部分重點：

```
TravelProjectDjango/
├── travelProject/            # Django 專案根目錄
│   ├── accounts/             # 帳號相關 app
│   ├── bookkeeping/          # 記帳相關 app
│   ├── camaramap/            # Google 地圖整合 app
│   ├── personalPage/         # 個人頁面 app
│   ├── trends_app/           # 熱門趨勢分析 app
│   └── manage.py             # Django 管理腳本
├── scripts/                  # 部署用 shell 腳本
└── requirements.txt          
```


## 其他

- `setup.ps1`、`setup.bat` 協助 Windows 使用者安裝 Python、 依賴。
- `hello_world.py` 為簡單範例程式。

歡迎依需求修改並擴充此專案。
