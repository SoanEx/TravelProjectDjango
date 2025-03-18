# PowerShell 腳本：產生專案的樹狀結構，並排除 .venv 目錄
# 儲存結果到 project_structure.txt
# 作者：你自己的名字
# 版本：1.0

function Tree {
    param (
        [string]$Path = ".",  # 預設從當前目錄開始
        [string]$Prefix = ""   # 用於控制輸出格式的前綴
    )

    # 取得當前目錄下的所有檔案與資料夾，並排除 .venv 目錄
    $items = Get-ChildItem -Path $Path -Exclude ".venv","jdk-23.0.2","assets" | Sort-Object Name
    $count = $items.Count
    $output = @()  # 用來存儲輸出內容

    for ($i = 0; $i -lt $count; $i++) {
        $item = $items[$i]

        # 選擇要顯示的分隔符號（├── 或 └──）
        $connector = if ($i -eq $count - 1) { "└──" } else { "├──" }
        
        # 儲存當前檔案或資料夾的名稱
        $output += "$Prefix$connector $($item.Name)"

        # 如果是資料夾，則遞迴處理內部內容，並加入輸出
        if ($item.PSIsContainer) {
            $output += Tree -Path $item.FullName -Prefix "$Prefix$(if ($i -eq $count - 1) { "    " } else { "│   " })"
        }
    }

    return $output
}

# 讓 PowerShell 以 UTF-8 編碼輸出
$OutputFile = "project_structure.txt"
$Utf8NoBom = New-Object System.Text.UTF8Encoding $false
$TreeOutput = Tree  # 執行 Tree 並捕捉輸出
[System.IO.File]::WriteAllLines($OutputFile, $TreeOutput, $Utf8NoBom)

# 顯示訊息
Write-Output "專案結構已輸出到 project_structure.txt（UTF-8 編碼）"