# 生日提醒應用

這是一個簡單的生日提醒應用，可以記錄朋友的農曆或西曆生日，並生成ICS檔案匯入到手機日曆中，獲得生日提醒。

## 功能特點

- 支持農曆和西曆生日記錄
- 可以設定生成ICS檔案的年份範圍
- 簡潔直觀的用戶界面
- 數據持久化存儲

## 技術棧

- Flask: Web框架
- Bootstrap 5: 前端UI框架
- ics: 生成ICS日曆檔案
- lunardate: 農曆日期轉換

## 部署到Render

### 前置條件

1. 擁有一個[Render](https://render.com)帳號
2. 將代碼推送到GitHub或GitLab倉庫

### 部署步驟

1. 登入Render帳號
2. 點擊「New」按鈕，選擇「Web Service」
3. 連接到您的GitHub或GitLab倉庫
4. 設定以下配置：
   - Name: 自定義服務名稱
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. 點擊「Create Web Service」按鈕

部署完成後，Render會提供一個URL，您可以通過該URL訪問應用。

## 本地開發

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動應用
python app.py
```

訪問 http://localhost:5000 即可使用應用。