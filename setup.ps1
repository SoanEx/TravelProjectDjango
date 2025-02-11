# 啟用錯誤停止
$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting project initialization and environment setup..."

# 1️⃣ 檢查是否安裝 pyenv，否則安裝 pyenv
if (-not (Get-Command pyenv -ErrorAction SilentlyContinue)) {
    Write-Host "🔧 Installing pyenv..."
    Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"
    & "./install-pyenv-win.ps1"
}

# 2️⃣ 確保安裝 Python 3.10.11
Write-Host "🔧 Checking and installing Python 3.10.11..."
if (-not (pyenv versions | Select-String "3.10.11")) {
    pyenv install 3.10.11
}
pyenv global 3.10.11

# 檢查 Python 版本
$pythonPath = python -c "import sys; print(sys.executable)"
if (-not $pythonPath) {
    Write-Host "❌ Python installation failed. Please check your setup." -ForegroundColor Red
    exit
} else {
    Write-Host "✅ Python installed successfully at $pythonPath" -ForegroundColor Green
}

# 3️⃣ 安裝 Poetry
if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing Poetry..."
    pip install poetry
}
poetry --version

# 4️⃣ 安裝專案依賴
Write-Host "📦 Installing project dependencies using Poetry..."
poetry install --no-root

# 5️⃣ 生成 requirements.txt（確保成員用 pip 也能管理依賴）
Write-Host "🔄 Exporting dependencies to requirements.txt..."
poetry export -f requirements.txt --output requirements.txt --without-hashes

# 6️⃣ 初始化 Git 並切換到 main 分支
if (-not (Test-Path ".git")) {
    Write-Host "🔗 Initializing Git repository..."
    git init
    git remote add origin https://github.com/SoanEx/TravelProjectDjango.git  # 替換為你的 Git URL
}

Write-Host "🔄 Fetching latest changes from main branch..."
git fetch origin
git checkout -b main origin/main

# 7️⃣ 確認所有文件加入 Git 並提交
Write-Host "🔗 Adding all changes to Git..."
git add .
git commit -m "Initial project setup with dependencies"

Write-Host "✅ Pushing changes to main branch..."
git push origin main

Write-Host "🎉 Project setup completed and changes pushed to main branch." -ForegroundColor Green
