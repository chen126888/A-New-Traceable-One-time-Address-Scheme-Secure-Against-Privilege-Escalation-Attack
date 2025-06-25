# Stealth Transaction System

基於PBC庫的匿名交易系統Flask後端

## 快速開始

1. 安裝依賴：
```bash
pip install -r requirements.txt
```

2. 編譯C庫：
```bash
cd c_lib
make
```

3. 運行應用：
```bash
python run.py
```

## API端點

- `/api/transaction/create` - 創建交易
- `/api/transaction/verify` - 驗證交易  
- `/api/trace/identity` - 身份追蹤

## 項目結構

詳見自動生成的目錄結構
