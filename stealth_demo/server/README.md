# Stealth Demo Server - Refactored

重構後的模塊化Stealth密碼學演示服務器。

## 架構說明

### 模塊結構

```
server/
├── app_refactored.py    # 主應用程式 (51行)
├── config.py           # 配置與狀態管理 (95行) 
├── library_wrapper.py  # C函式庫包裝器 (167行)
├── crypto_services.py  # 密碼學服務 (334行)
├── utils.py           # 工具函式 (64行)
├── routes.py          # API路由 (165行)
├── run.py             # 簡單啟動腳本
└── __init__.py        # 套件初始化
```

### 原本vs重構後

- **原本**: 單一 `app.py` 檔案 (824行)
- **重構後**: 7個模塊，職責分離，易於維護

## 運行方式

### 方式1: 直接執行
```bash
cd server/
python3 app_refactored.py
```

### 方式2: 使用啟動腳本
```bash
cd server/
python3 run.py
```

### 方式3: 使用原本的app.py (未更改)
```bash
cd server/
python3 app.py
```

## 模塊說明

### 1. `config.py` - 配置管理
- 系統初始化狀態
- 參數檔案處理
- 全局資料存儲
- 狀態驗證

### 2. `library_wrapper.py` - C函式庫包裝
- 動態函式庫載入
- 函式簽名設定
- 低階C函式封裝
- DSK功能檢測

### 3. `crypto_services.py` - 密碼學服務
- 系統初始化
- 密鑰生成
- 位址生成與驗證
- 簽章與驗證
- 身份追蹤
- 效能測試

### 4. `utils.py` - 工具函式
- 十六進制/位元組轉換
- 緩衝區管理
- 索引驗證
- 輔助函式

### 5. `routes.py` - API路由
- Flask路由定義
- 請求處理
- 錯誤處理
- 回應格式化

### 6. `app_refactored.py` - 主應用程式
- Flask應用程式創建
- 全局錯誤處理
- 靜態檔案服務
- 應用程式啟動

## 優勢

1. **模塊化**: 每個模塊職責單一
2. **可維護性**: 易於理解和修改
3. **可測試性**: 各模塊可獨立測試
4. **可擴展性**: 新功能易於添加
5. **可重用性**: 模塊可在其他專案使用

## API端點

所有原本的API端點保持不變：

- `GET /param_files` - 取得參數檔案列表
- `POST /setup` - 初始化系統
- `GET /keygen` - 生成密鑰對
- `GET /keylist` - 取得密鑰列表
- `POST /addrgen` - 生成位址
- `GET /addresslist` - 取得位址列表
- `POST /verify_addr` - 驗證位址
- `POST /dskgen` - 生成DSK
- `GET /dsklist` - 取得DSK列表
- `POST /sign` - 簽章訊息
- `POST /verify_signature` - 驗證簽章
- `POST /trace` - 追蹤身份
- `POST /performance_test` - 效能測試
- `GET /status` - 系統狀態
- `POST /reset` - 重設系統
- `GET /tx_messages` - 取得交易訊息