# 🧾 台灣統一發票助手 (mcp-tw-invoice)

這是一個基於 **FastMCP** 框架開發的 Model Context Protocol (MCP) 伺服器，支援查詢台灣統一發票中獎號碼與自動對獎。

## ✨ 特點
- **FastMCP 架構**：使用最新 FastMCP 框架，程式碼簡潔且效能穩定。
- **雙傳輸模式**：同時支援 `stdio` (本機) 與 `streamable-http` (遠端/Docker) 模式。
- **自動對獎**：輸入末 3 碼或完整 8 碼即可判斷是否中獎。

---

## 🚀 傳輸模式 (Transport Modes)

### 1. 本機模式 (STDIO) - 預設
適合在個人電腦上與 Claude Desktop 搭配使用。
```bash
python src/server.py --mode stdio
```

### 2. 遠端模式 (HTTP)
適合 Docker 部署與 Dive 客戶端連線。
```bash
python src/server.py --mode http --port 8000
```
- **服務 URL**: `http://localhost:8000/mcp`

---

## 🛠️ 安裝與啟動

### 1. 本機安裝
```bash
pip install .
```

### 2. Docker 啟動 (推薦)
```bash
docker build -t mcp-tw-invoice .
docker run -p 8000:8000 mcp-tw-invoice
```

---

## 🔌 客戶端配置範例

### Claude Desktop (STDIO)
```json
{
  "mcpServers": {
    "tw-invoice": {
      "command": "python",
      "args": ["/絕對路徑/src/server.py", "--mode", "stdio"]
    }
  }
}
```

### Dive / HTTP 客戶端
- **Type**: `streamable`
- **URL**: `http://localhost:8000/mcp`

---

## 📄 免責聲明
本工具提供之資訊僅供參考，中獎號碼請以財政部稅務入口網公佈之資料為準。
