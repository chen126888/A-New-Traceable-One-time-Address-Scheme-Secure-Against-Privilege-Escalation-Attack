# Multi-Scheme Backend Server

重構後的模塊化後端架構，支援5個密碼學方案的動態切換。

## 📁 目錄結構

```
server/
├── app.py                 # 主應用入口點
├── app_factory.py         # Flask應用工廠
├── config.py             # 應用配置和狀態管理
├── scheme_manager.py     # 方案管理器 (核心)
├── frontend_routes.py    # 前端靜態文件服務
├── api/                  # API模塊
│   ├── __init__.py      
│   ├── routes.py        # 主要API路由
│   └── schemes.py       # 方案管理路由
└── README.md            # 本說明文件
```

## 🚀 啟動方式

```bash
# 方式1: 從項目根目錄運行
python3 server/app.py

# 方式2: 從server目錄運行 (自動切換到項目根目錄)
cd server && python3 app.py
```

**智能路徑檢測**: 程序會自動檢測運行位置並切換到正確的項目根目錄！

## 📊 支援的方案

| Scheme | Type | Functions | Status |
|--------|------|-----------|---------|
| my_stealth | PBC | 10 | ✅ Available |
| cryptonote2 | ECC | 7 | ✅ Available |
| zhao | ECC | 6 | ✅ Available |
| hdwsa | PBC | 8 | ✅ Available |
| sitaiba | PBC | 8 | ✅ Available |

## 🔧 模塊說明

### 1. `app.py` - 主入口
- 檢查運行環境
- 創建應用實例
- 啟動服務器

### 2. `app_factory.py` - 應用工廠
- 創建Flask應用
- 註冊所有藍圖
- 配置CORS和錯誤處理
- 打印啟動信息

### 3. `config.py` - 配置管理
- 應用配置類 `Config`
- 演示狀態管理類 `DemoState`
- 路徑驗證功能

### 4. `api/routes.py` - 主要API
- `/api/status` - 系統狀態
- `/api/param_files` - 參數文件列表
- `/api/setup` - 系統初始化
- `/api/keygen` - 密鑰生成
- `/api/keylist` - 密鑰列表
- `/api/reset` - 系統重置

### 5. `api/schemes.py` - 方案管理API
- `/schemes` - 獲取可用方案
- `/schemes/<id>` - 切換方案

### 6. `frontend_routes.py` - 前端服務
- `/` - React應用主頁
- `/<path>` - 靜態文件服務

## 🔌 API端點

### 方案管理
```
GET  /schemes           # 獲取所有可用方案
POST /schemes/{id}      # 切換到指定方案
```

### 系統控制
```
GET  /api/status        # 系統狀態
GET  /api/param_files   # 參數文件列表
POST /api/setup         # 初始化系統
POST /api/reset         # 重置系統
```

### 密鑰管理
```
GET  /api/keygen        # 生成新密鑰
GET  /api/keylist       # 獲取密鑰列表
```

## 🛠️ 開發指南

### 添加新的API端點
1. 在 `api/routes.py` 中添加路由函數
2. 使用 `scheme_manager` 和 `demo_state` 參數
3. 返回標準JSON格式

### 添加新的方案支援
1. 在 `c_src/` 中添加方案目錄
2. 更新 `scheme_manager.py` 的 `SCHEMES` 配置
3. 編譯新的共享庫到 `lib/`

### 修改配置
1. 在 `config.py` 中更新 `Config` 類
2. 路徑、緩衝區大小等設置都在這裡

## 🧪 測試

```bash
# 檢查所有方案是否可用
curl http://localhost:5000/schemes

# 切換到特定方案
curl -X POST http://localhost:5000/schemes/cryptonote2

# 檢查系統狀態
curl http://localhost:5000/api/status
```