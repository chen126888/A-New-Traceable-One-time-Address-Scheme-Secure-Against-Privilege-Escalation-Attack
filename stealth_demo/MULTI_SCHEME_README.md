# 🔐 Multi-Scheme Stealth Demo

多方案密碼學演示系統，支援五種不同的匿名交易方案比較和測試。

## 🏗️ 架構概述

### 支援的方案
1. **My Stealth** - 原始的可追蹤匿名交易方案 (✅ 已實現)
2. **CryptoNote2** - CryptoNote v2 協議 (❌ 待添加)
3. **Zhao** - Zhao等人的方案 (❌ 待添加)
4. **HDWSA** - 階層式確定性錢包簽章演算法 (❌ 待添加)
5. **Sitaiba** - Sitaiba等人的方案 (❌ 待添加)

### 目錄結構
```
stealth_demo/
├── c_src/                      # C源碼目錄
│   ├── my_stealth/            # My Stealth方案 ✅
│   │   ├── my_scheme_core.c
│   │   ├── my_scheme_core.h
│   │   ├── python_api.c
│   │   ├── python_api.h
│   │   └── Makefile
│   ├── cryptonote2/           # 待添加
│   ├── zhao/                  # 待添加
│   ├── hdwsa/                 # 待添加
│   ├── sitaiba/               # 待添加
│   └── Makefile              # 主編譯檔案
│
├── lib/                       # 編譯後的共享庫
│   ├── libmy_stealth.so      # ✅ 已編譯
│   ├── libcryptonote2.so     # 待編譯
│   ├── libzhao.so            # 待編譯
│   ├── libhdwsa.so           # 待編譯
│   └── libsitaiba.so         # 待編譯
│
├── param/                     # 參數檔案
│   ├── *.param               # PBC參數 (my_stealth, hdwsa, sitaiba)
│   └── ecc_params/           # ECC參數 (cryptonote2, zhao)
│
├── server/                    # Python後端
│   ├── app_multi_scheme.py   # 新的多方案後端
│   ├── scheme_manager.py     # 方案管理器
│   └── app.py               # 原始後端 (備用)
│
└── frontend-react/            # React前端
    └── src/components/
        └── SchemeSelector.jsx # 方案選擇器
```

## 🚀 快速開始

### 1. 編譯系統
```bash
cd c_src
make help          # 查看可用指令
make status        # 查看編譯狀態
make all          # 編譯所有可用方案
make my_stealth   # 只編譯My Stealth方案
```

### 2. 啟動後端服務
```bash
cd server
python3 app_multi_scheme.py
```

### 3. 啟動前端
```bash
cd frontend-react
npm run dev
```

### 4. 使用方法
1. 打開 http://localhost:3000
2. 在方案選擇器中選擇要使用的密碼學方案
3. 點擊「Select」切換方案
4. 在SystemSetup中初始化方案
5. 開始使用各種密碼學操作

## 🔧 編譯系統

### 主要指令
- `make all` - 編譯所有可用方案
- `make <scheme>` - 編譯特定方案
- `make status` - 查看所有方案狀態
- `make clean` - 清理編譯產物
- `make check` - 檢查已編譯的庫

### 範例輸出
```bash
$ make status
📊 Multi-Scheme Build Status
==================================
my_stealth  : ✅ Built
cryptonote2 : ❌ Not available
zhao        : ❌ Not available
hdwsa       : ❌ Not available
sitaiba     : ❌ Not available
```

## 🔌 API接口

### 新增的多方案API
- `GET /schemes` - 取得可用方案列表
- `POST /schemes/<scheme_id>` - 切換到指定方案
- `GET /status` - 取得系統狀態（包含當前方案）

### 原有API (支援動態方案)
- `GET /param_files` - 取得參數檔案（根據當前方案）
- `POST /setup` - 初始化當前方案
- `GET /keygen` - 產生金鑰對
- 其他密碼學操作...

## 📝 添加新方案

### 步驟1: 準備源碼
```bash
mkdir c_src/<scheme_name>
# 添加以下檔案到目錄：
# - core.c, core.h (核心實現)
# - python_api.c, python_api.h (Python介面)
# - Makefile
```

### 步驟2: 實現統一API
每個方案需要實現以下函數：
```c
// 基本函數 (所有方案都需要)
int <scheme>_init(const char* param_file);
void <scheme>_keygen_simple(unsigned char* A_out, ...);

// 可選函數 (根據方案特性)
void <scheme>_addr_gen_simple(...);     // 地址生成
int <scheme>_addr_verify_simple(...);   // 地址驗證  
void <scheme>_sign_simple(...);         // 簽章
int <scheme>_verify_simple(...);        // 驗證
void <scheme>_trace_simple(...);        // 追蹤 (如果支援)
```

### 步驟3: 更新配置
在 `server/scheme_manager.py` 中添加方案配置：
```python
SCHEMES = {
    'new_scheme': {
        'lib_name': 'libnew_scheme.so',
        'display_name': 'New Scheme Name',
        'description': 'Description of the new scheme',
        'functions': ['init', 'keygen', 'sign', 'verify'],
        'param_type': 'pbc',  # or 'ecc'
        'function_prefix': 'new_scheme_'
    }
}
```

### 步驟4: 編譯和測試
```bash
make new_scheme      # 編譯新方案
make status          # 檢查狀態
```

## 🎯 功能支援矩陣

| 方案 | 金鑰生成 | 地址生成 | 地址驗證 | 簽章 | 驗證 | 追蹤 | 參數類型 |
|------|----------|----------|----------|------|------|------|----------|
| My Stealth | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | PBC |
| CryptoNote2 | ❓ | ❓ | ❓ | ❓ | ❓ | ❌ | ECC |
| Zhao | ❓ | ❌ | ❌ | ❓ | ❓ | ❌ | ECC |
| HDWSA | ❓ | ❌ | ❌ | ❓ | ❓ | ❌ | PBC |
| Sitaiba | ❓ | ❓ | ❓ | ❓ | ❓ | ❓ | PBC |

*❓ = 待實現，❌ = 不支援，✅ = 已實現*

## 🔍 故障排除

### 編譯問題
```bash
# 檢查依賴
sudo apt-get install libpbc-dev libgmp-dev libssl-dev

# 檢查庫載入
make check
```

### 運行問題
```bash
# 檢查Python依賴
pip install flask

# 檢查前端依賴
cd frontend-react && npm install
```

### 常見錯誤
- **"No scheme loaded"** - 需要先在前端選擇方案
- **"Library not found"** - 需要先編譯對應的方案
- **"Scheme not initialized"** - 需要在SystemSetup中初始化

## 📈 性能比較

計劃中的功能：跨方案性能比較頁面，可以：
- 同時測試所有可用方案
- 產生性能比較圖表
- 匯出比較結果

## 🤝 貢獻

歡迎添加新的密碼學方案！請參考上述「添加新方案」章節。

---

**注意**: 目前只有 My Stealth 方案完全可用，其他方案需要您提供對應的C源碼才能啟用。