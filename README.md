# TravelProjectDjango

本專案是一個使用 **Django** 與 **Poetry** 管理後端相依套件的示範專案，
同時包含 React 前端 (位於 `travelProject/personalpage-frontend`) 與多個 Django app。
倉庫內也附有 AWS CodeDeploy 的腳本，方便部署至 EC2。

## 環境需求

- Python 3.10 以上（建議 3.10.11）
- [Poetry](https://python-poetry.org/) 用於安裝與管理依賴
- Node.js 18 以上（如需啟動前端）

## 專案初始化

1. 下載專案並切換到目錄：
   ```bash
   git clone <repo-url>
   cd TravelProjectDjango
   ```
2. 安裝後端依賴：
   ```bash
   poetry install
   ```
   或使用 `pip install -r requirements.txt`。
3. 複製 `.env` 檔並填入必要設定，常見變數如下：
   ```env
   DJANGO_SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   DB_NAME=your_db
   DB_USER=your_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=3306
   OPENAI_API_KEY=your-openai-key
   ```
4. 進行資料庫遷移與收集靜態檔案：
   ```bash
   poetry run python travelProject/manage.py migrate
   poetry run python travelProject/manage.py collectstatic --noinput
   ```

## 啟動開發伺服器

執行下列指令即可開啟本地伺服器：
```bash
poetry run python travelProject/manage.py runserver
```
預設會在 `http://127.0.0.1:8000/` 提供服務。

若要啟動 React 前端，進入 `travelProject/personalpage-frontend` 後執行：
```bash
npm install
npm start
```

## 測試

專案內含多個 Django app 的測試，可透過：
```bash
poetry run python travelProject/manage.py test
```
執行測試。若環境未安裝所有依賴，測試可能無法順利進行。

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
├── requirements.txt          # 由 Poetry 匯出的依賴列表
└── pyproject.toml            # Poetry 設定檔
```

## 其他

- `setup.ps1`、`setup.bat` 為 Windows 使用者準備的初始化腳本，可協助安裝 Python、Poetry 及相關依賴。
- `hello_world.py` 為簡易範例腳本。

歡迎依需求修改並擴充此專案。
