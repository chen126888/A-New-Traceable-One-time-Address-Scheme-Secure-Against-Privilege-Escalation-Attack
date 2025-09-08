# A New Traceable One-time Address Scheme Secure Against Privilege Escalation Attack

這是我碩士論文「A New Traceable One-time Address Scheme Secure Against Privilege Escalation Attack」的程式碼 repo。

裡面主要放了論文中提出方案的 C 語言實作，以及一些用來做效能比較的相关方案。

## 檔案結構

* `Traceable_One-time_Address_Scheme/schemes/`
    * 這裏是 C 語言的核心程式碼，主要使用pbc library，包含我提出的方案跟其他對照組。
* `demo/`
    * 一個用 Python Flask 寫的簡單前端。
    * 目標是做一個網頁介面，讓大家可以直接在瀏覽器上跑各個方案的演算法、看看輸出結果，順便量一下執行時間。
    * server: python3 app.py
    * frontend-react: npm run dev

## 開發進度

目前 `demo/` 的測試環境中，已經可以玩我自己寫的這兩個方案了：

* **Stealth 方案** (投稿後改進的版本)
* **Sitaiba 方案** (投稿用的版本)

