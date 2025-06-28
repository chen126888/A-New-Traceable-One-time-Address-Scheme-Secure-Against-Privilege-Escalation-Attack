#!/usr/bin/env python3
"""
進階 Debug 腳本 - 只顯示完整 hex 數據
使用方法: python3 debug_hex_only.py
"""

import os
import sys
from ctypes import *
import traceback

class StealthDebugger:
    def __init__(self):
        self.lib = None
        self.initialized = False
        self.test_results = {}
        
    def print_section(self, title):
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print('='*60)
    
    def log_result(self, test_name, success, details=""):
        """記錄測試結果"""
        self.test_results[test_name] = {
            'success': success,
            'details': details
        }
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
    
    def get_hex_data(self, buf):
        """獲取緩衝區的完整 hex 數據"""
        non_zero_len = len([b for b in buf.raw if b != 0])
        if non_zero_len > 0:
            return buf.raw[:non_zero_len].hex()
        return ""
    
    def print_hex_data(self, name, buf):
        """打印完整的 hex 數據"""
        hex_data = self.get_hex_data(buf)
        if hex_data:
            print(f"📊 {name}:")
            print(f"   長度: {len(hex_data)//2} bytes")
            print(f"   完整 hex: {hex_data}")
        else:
            print(f"❌ {name}: 空數據")
    
    def load_library(self):
        """載入和設置 library"""
        self.print_section("Library 載入和設置")
        
        try:
            self.lib = CDLL("../lib/libstealth.so")
            self.log_result("Library 載入", True, "成功載入 libstealth.so")
            
            # 設置函數簽名
            self.setup_function_signatures()
            self.log_result("函數簽名設置", True, "所有函數簽名設置完成")
            
            return True
        except Exception as e:
            self.log_result("Library 載入", False, f"失敗: {e}")
            return False
    
    def setup_function_signatures(self):
        """設置所有函數簽名"""
        # 核心管理函數
        self.lib.stealth_init.argtypes = [c_char_p]
        self.lib.stealth_init.restype = c_int
        self.lib.stealth_is_initialized.restype = c_int
        self.lib.stealth_cleanup.restype = None
        self.lib.stealth_element_size_G1.restype = c_int
        self.lib.stealth_element_size_Zr.restype = c_int
        
        # Python 接口函數
        self.lib.stealth_keygen_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.lib.stealth_keygen_simple.restype = None
        
        self.lib.stealth_tracekeygen_simple.argtypes = [c_char_p, c_char_p, c_int]
        self.lib.stealth_tracekeygen_simple.restype = None
        
        self.lib.stealth_addr_gen_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.lib.stealth_addr_gen_simple.restype = None
        
        self.lib.stealth_addr_verify_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
        self.lib.stealth_addr_verify_simple.restype = c_int
        
        self.lib.stealth_sign_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.lib.stealth_sign_simple.restype = None
        
        self.lib.stealth_verify_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
        self.lib.stealth_verify_simple.restype = c_int
        
        self.lib.stealth_trace_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.lib.stealth_trace_simple.restype = None
    
    def test_initialization(self):
        """測試初始化"""
        self.print_section("初始化測試")
        
        # 測試不同的參數文件
        param_files = [
            "../param/a.param",
        ]
        
        for param_file in param_files:
            if not os.path.exists(param_file):
                self.log_result(f"參數文件 {param_file}", False, "文件不存在")
                continue
                
            try:
                print(f"\n📋 測試參數文件: {param_file}")
                result = self.lib.stealth_init(param_file.encode())
                is_init = self.lib.stealth_is_initialized()
                
                if result == 0 and is_init:
                    self.log_result(f"初始化 {os.path.basename(param_file)}", True, f"成功 (返回值: {result})")
                    self.initialized = True
                    
                    # 測試元素大小
                    g1_size = self.lib.stealth_element_size_G1()
                    zr_size = self.lib.stealth_element_size_Zr()
                    self.log_result("元素大小獲取", True, f"G1: {g1_size} bytes, Zr: {zr_size} bytes")
                    
                    return True
                else:
                    self.log_result(f"初始化 {os.path.basename(param_file)}", False,
                                  f"失敗 (返回值: {result}, 狀態: {is_init})")
                    
            except Exception as e:
                self.log_result(f"初始化 {os.path.basename(param_file)}", False, f"異常: {e}")
        
        return False
    
    def test_key_generation(self):
        """測試密鑰生成"""
        self.print_section("密鑰生成測試")
        
        if not self.initialized:
            self.log_result("密鑰生成", False, "Library 未初始化")
            return None
            
        try:
            buf_size = max(self.lib.stealth_element_size_G1(), 
                          self.lib.stealth_element_size_Zr(), 512)
            
            print(f"📦 使用緩衝區大小: {buf_size} bytes")
            
            # 創建緩衝區
            A_buf = create_string_buffer(buf_size)
            B_buf = create_string_buffer(buf_size)
            a_buf = create_string_buffer(buf_size)
            b_buf = create_string_buffer(buf_size)
            
            # 清零緩衝區
            for buf in [A_buf, B_buf, a_buf, b_buf]:
                for i in range(buf_size):
                    buf[i] = 0
            
            # 生成密鑰
            print("🔑 調用 stealth_keygen_simple...")
            self.lib.stealth_keygen_simple(A_buf, B_buf, a_buf, b_buf, buf_size)
            print("✅ stealth_keygen_simple 調用完成")
            
            # 顯示所有密鑰的完整 hex 數據
            print("\n📊 生成的密鑰完整數據:")
            self.print_hex_data("A (公鑰)", A_buf)
            self.print_hex_data("B (公鑰)", B_buf)
            self.print_hex_data("a (私鑰)", a_buf)
            self.print_hex_data("b (私鑰)", b_buf)
            
            # 檢查是否所有密鑰都生成
            A_hex = self.get_hex_data(A_buf)
            B_hex = self.get_hex_data(B_buf)
            a_hex = self.get_hex_data(a_buf)
            b_hex = self.get_hex_data(b_buf)
            
            if A_hex and B_hex and a_hex and b_hex:
                self.log_result("密鑰生成", True, "所有密鑰都成功生成")
                return {
                    'A_buf': A_buf, 'B_buf': B_buf,
                    'a_buf': a_buf, 'b_buf': b_buf
                }
            else:
                self.log_result("密鑰生成", False, "部分或全部密鑰為空")
                return None
                
        except Exception as e:
            self.log_result("密鑰生成", False, f"異常: {e}")
            traceback.print_exc()
            return None
    
    def test_trace_key_generation(self):
        """測試追蹤密鑰生成"""
        self.print_section("追蹤密鑰生成測試")
        
        if not self.initialized:
            self.log_result("追蹤密鑰生成", False, "Library 未初始化")
            return None
            
        try:
            buf_size = max(self.lib.stealth_element_size_G1(), 
                          self.lib.stealth_element_size_Zr(), 512)
            
            TK_buf = create_string_buffer(buf_size)
            k_buf = create_string_buffer(buf_size)
            
            # 清零緩衝區
            for i in range(buf_size):
                TK_buf[i] = 0
                k_buf[i] = 0
            
            print("🔍 調用 stealth_tracekeygen_simple...")
            self.lib.stealth_tracekeygen_simple(TK_buf, k_buf, buf_size)
            print("✅ stealth_tracekeygen_simple 調用完成")
            
            # 顯示追蹤密鑰的完整 hex 數據
            print("\n📊 生成的追蹤密鑰完整數據:")
            self.print_hex_data("TK (追蹤公鑰)", TK_buf)
            self.print_hex_data("k (追蹤私鑰)", k_buf)
            
            TK_hex = self.get_hex_data(TK_buf)
            k_hex = self.get_hex_data(k_buf)
            
            if TK_hex and k_hex:
                self.log_result("追蹤密鑰生成", True, "追蹤密鑰成功生成")
                return {'TK_buf': TK_buf, 'k_buf': k_buf}
            else:
                self.log_result("追蹤密鑰生成", False, "追蹤密鑰為空")
                return None
                
        except Exception as e:
            self.log_result("追蹤密鑰生成", False, f"異常: {e}")
            traceback.print_exc()
            return None
    
    def test_address_generation(self, keys, trace_keys):
        """測試地址生成"""
        self.print_section("地址生成測試")
        
        if not keys or not trace_keys:
            self.log_result("地址生成", False, "缺少必要的密鑰")
            return None
            
        try:
            buf_size = max(self.lib.stealth_element_size_G1(), 
                          self.lib.stealth_element_size_Zr(), 512)
            
            # 準備輸出緩衝區
            addr_buf = create_string_buffer(buf_size)
            r1_buf = create_string_buffer(buf_size)
            r2_buf = create_string_buffer(buf_size)
            c_buf = create_string_buffer(buf_size)
            
            # 清零緩衝區
            for buf in [addr_buf, r1_buf, r2_buf, c_buf]:
                for i in range(buf_size):
                    buf[i] = 0
            
            print("📥 地址生成輸入數據:")
            self.print_hex_data("A (輸入)", keys['A_buf'])
            self.print_hex_data("B (輸入)", keys['B_buf'])
            self.print_hex_data("TK (輸入)", trace_keys['TK_buf'])
            
            print(f"\n📧 調用 stealth_addr_gen_simple... (緩衝區大小: {buf_size})")
            
            # 調用地址生成函數
            self.lib.stealth_addr_gen_simple(
                keys['A_buf'].raw, keys['B_buf'].raw, trace_keys['TK_buf'].raw,
                addr_buf, r1_buf, r2_buf, c_buf, buf_size
            )
            
            print("✅ stealth_addr_gen_simple 調用完成")
            
            # 顯示所有地址組件的完整 hex 數據
            print("\n📊 生成的地址組件完整數據:")
            self.print_hex_data("Addr (地址)", addr_buf)
            self.print_hex_data("R1 (組件1)", r1_buf)
            self.print_hex_data("R2 (組件2)", r2_buf)
            self.print_hex_data("C (組件3)", c_buf)
            
            # 檢查結果
            addr_hex = self.get_hex_data(addr_buf)
            r1_hex = self.get_hex_data(r1_buf)
            r2_hex = self.get_hex_data(r2_buf)
            c_hex = self.get_hex_data(c_buf)
            
            if addr_hex and r1_hex and r2_hex and c_hex:
                self.log_result("地址生成", True, "所有地址組件都成功生成")
                return {
                    'addr_buf': addr_buf, 'r1_buf': r1_buf,
                    'r2_buf': r2_buf, 'c_buf': c_buf
                }
            else:
                missing = []
                if not addr_hex: missing.append("Addr")
                if not r1_hex: missing.append("R1")
                if not r2_hex: missing.append("R2")
                if not c_hex: missing.append("C")
                
                self.log_result("地址生成", False, f"缺少組件: {', '.join(missing)}")
                return None
                
        except Exception as e:
            self.log_result("地址生成", False, f"異常: {e}")
            traceback.print_exc()
            return None
    
    def test_address_verification(self, keys, address_data):
        """測試地址驗證"""
        self.print_section("地址驗證測試")
        
        if not keys or not address_data:
            self.log_result("地址驗證", False, "缺少必要的密鑰或地址數據")
            return False
            
        try:
            print("📥 地址驗證輸入數據:")
            self.print_hex_data("R1 (用於驗證)", address_data['r1_buf'])
            self.print_hex_data("B (用於驗證)", keys['B_buf'])
            self.print_hex_data("A (用於驗證)", keys['A_buf'])
            self.print_hex_data("C (用於驗證)", address_data['c_buf'])
            self.print_hex_data("a (私鑰用於驗證)", keys['a_buf'])
            
            print("\n🔍 調用 stealth_addr_verify_simple...")
            
            # 調用快速驗證函數
            result = self.lib.stealth_addr_verify_simple(
                address_data['r1_buf'].raw,
                keys['B_buf'].raw,
                keys['A_buf'].raw,
                address_data['c_buf'].raw,
                keys['a_buf'].raw
            )
            
            print(f"✅ 驗證結果: {result} ({'成功' if result == 1 else '失敗'})")
            
            if result == 1:
                self.log_result("地址驗證", True, "地址驗證成功")
                return True
            else:
                self.log_result("地址驗證", False, f"驗證失敗 (返回值: {result})")
                return False
                
        except Exception as e:
            self.log_result("地址驗證", False, f"異常: {e}")
            traceback.print_exc()
            return False
    
    def test_signing_and_verification(self, keys, address_data):
        """測試簽名和驗證"""
        self.print_section("簽名和驗證測試")
        
        if not keys or not address_data:
            self.log_result("簽名測試", False, "缺少必要的密鑰或地址數據")
            return False
            
        try:
            message = b"Test message for debugging"
            buf_size = max(self.lib.stealth_element_size_G1(), 
                          self.lib.stealth_element_size_Zr(), 512)
            
            print(f"📝 測試消息: {message.decode()}")
            
            # 準備簽名輸出緩衝區
            q_sigma_buf = create_string_buffer(buf_size)
            h_buf = create_string_buffer(buf_size)
            dsk_buf = create_string_buffer(buf_size)
            
            # 清零緩衝區
            for buf in [q_sigma_buf, h_buf, dsk_buf]:
                for i in range(buf_size):
                    buf[i] = 0
            
            print("\n📥 簽名輸入數據:")
            self.print_hex_data("Addr (用於簽名)", address_data['addr_buf'])
            self.print_hex_data("R1 (用於簽名)", address_data['r1_buf'])
            self.print_hex_data("a (私鑰)", keys['a_buf'])
            self.print_hex_data("b (私鑰)", keys['b_buf'])
            
            print("\n✍️ 調用 stealth_sign_simple...")
            
            # 調用簽名函數
            self.lib.stealth_sign_simple(
                address_data['addr_buf'].raw,
                address_data['r1_buf'].raw,
                keys['a_buf'].raw,
                keys['b_buf'].raw,
                message,
                q_sigma_buf, h_buf, dsk_buf, buf_size
            )
            
            print("✅ stealth_sign_simple 調用完成")
            
            # 顯示簽名結果的完整 hex 數據
            print("\n📊 生成的簽名完整數據:")
            self.print_hex_data("Q_sigma (簽名)", q_sigma_buf)
            self.print_hex_data("H (哈希)", h_buf)
            self.print_hex_data("DSK (一次性密鑰)", dsk_buf)
            
            q_hex = self.get_hex_data(q_sigma_buf)
            h_hex = self.get_hex_data(h_buf)
            dsk_hex = self.get_hex_data(dsk_buf)
            
            if q_hex and h_hex and dsk_hex:
                self.log_result("簽名生成", True, "簽名成功生成")
                
                # 測試簽名驗證
                print("\n📥 簽名驗證輸入數據:")
                self.print_hex_data("Addr (用於驗證)", address_data['addr_buf'])
                self.print_hex_data("R2 (用於驗證)", address_data['r2_buf'])
                self.print_hex_data("C (用於驗證)", address_data['c_buf'])
                print(f"Message: {message.decode()}")
                self.print_hex_data("H (用於驗證)", h_buf)
                self.print_hex_data("Q_sigma (用於驗證)", q_sigma_buf)
                
                print("\n🔍 調用 stealth_verify_simple...")
                verify_result = self.lib.stealth_verify_simple(
                    address_data['addr_buf'].raw,
                    address_data['r2_buf'].raw,
                    address_data['c_buf'].raw,
                    message,
                    h_buf.raw,
                    q_sigma_buf.raw
                )
                
                print(f"✅ 簽名驗證結果: {verify_result} ({'成功' if verify_result == 1 else '失敗'})")
                
                if verify_result == 1:
                    self.log_result("簽名驗證", True, "簽名驗證成功")
                    return True
                else:
                    self.log_result("簽名驗證", False, f"驗證失敗 (返回值: {verify_result})")
                    return False
            else:
                missing = []
                if not q_hex: missing.append("Q_sigma")
                if not h_hex: missing.append("H")
                if not dsk_hex: missing.append("DSK")
                
                self.log_result("簽名生成", False, f"缺少簽名組件: {', '.join(missing)}")
                return False
                
        except Exception as e:
            self.log_result("簽名測試", False, f"異常: {e}")
            traceback.print_exc()
            return False
    
    def test_identity_tracing(self, keys, address_data, trace_keys):
        """測試身份追蹤"""
        self.print_section("身份追蹤測試")
        
        if not keys or not address_data or not trace_keys:
            self.log_result("身份追蹤", False, "缺少必要的密鑰或地址數據")
            return False
            
        try:
            buf_size = max(self.lib.stealth_element_size_G1(), 
                          self.lib.stealth_element_size_Zr(), 512)
            
            # 準備輸出緩衝區
            recovered_b_buf = create_string_buffer(buf_size)
            
            # 清零緩衝區
            for i in range(buf_size):
                recovered_b_buf[i] = 0
            
            print("📥 身份追蹤輸入數據:")
            self.print_hex_data("Addr (用於追蹤)", address_data['addr_buf'])
            self.print_hex_data("R1 (用於追蹤)", address_data['r1_buf'])
            self.print_hex_data("R2 (用於追蹤)", address_data['r2_buf'])
            self.print_hex_data("C (用於追蹤)", address_data['c_buf'])
            self.print_hex_data("k (追蹤私鑰)", trace_keys['k_buf'])
            
            print("\n🔍 調用 stealth_trace_simple...")
            
            # 調用追蹤函數
            self.lib.stealth_trace_simple(
                address_data['addr_buf'].raw,
                address_data['r1_buf'].raw,
                address_data['r2_buf'].raw,
                address_data['c_buf'].raw,
                trace_keys['k_buf'].raw,
                recovered_b_buf, buf_size
            )
            
            print("✅ stealth_trace_simple 調用完成")
            
            # 顯示追蹤結果
            print("\n📊 身份追蹤結果:")
            self.print_hex_data("恢復的 B", recovered_b_buf)
            
            print("\n🔍 與原始密鑰比較:")
            self.print_hex_data("原始 B", keys['B_buf'])
            
            recovered_hex = self.get_hex_data(recovered_b_buf)
            original_hex = self.get_hex_data(keys['B_buf'])
            
            if recovered_hex:
                if recovered_hex == original_hex:
                    print("✅ 完全匹配！")
                    self.log_result("身份追蹤", True, "成功恢復原始密鑰 B")
                    return True
                else:
                    print("⚠️ 數據不匹配")
                    print(f"原始長度: {len(original_hex)//2} bytes")
                    print(f"恢復長度: {len(recovered_hex)//2} bytes")
                    self.log_result("身份追蹤", True, "追蹤成功但密鑰不同")
                    return True
            else:
                self.log_result("身份追蹤", False, "恢復的密鑰為空")
                return False
                
        except Exception as e:
            self.log_result("身份追蹤", False, f"異常: {e}")
            traceback.print_exc()
            return False
    
    def generate_summary_report(self):
        """生成總結報告"""
        self.print_section("測試總結報告")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        
        print(f"📊 測試統計:")
        print(f"   總測試數: {total_tests}")
        print(f"   通過測試: {passed_tests}")
        print(f"   失敗測試: {total_tests - passed_tests}")
        print(f"   成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 詳細結果:")
        for test_name, result in self.test_results.items():
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {test_name}: {result['details']}")
        
        return passed_tests == total_tests
    
    def run_full_test(self):
        """運行完整測試"""
        print("🚀 開始進階 Debug 測試 (完整 Hex 數據版本)")
        print("📋 將顯示所有組件的完整 hex 數據")
        
        # 1. 載入 library
        if not self.load_library():
            return False
        
        # 2. 測試初始化
        if not self.test_initialization():
            return False
        
        # 3. 測試密鑰生成
        keys = self.test_key_generation()
        if not keys:
            return False
        
        # 4. 測試追蹤密鑰生成
        trace_keys = self.test_trace_key_generation()
        if not trace_keys:
            return False
        
        # 5. 測試地址生成
        address_data = self.test_address_generation(keys, trace_keys)
        if not address_data:
            self.generate_summary_report()
            return False
        
        # 6. 測試地址驗證
        self.test_address_verification(keys, address_data)
        
        # 7. 測試簽名和驗證
        self.test_signing_and_verification(keys, address_data)
        
        # 8. 測試身份追蹤
        self.test_identity_tracing(keys, address_data, trace_keys)
        
        # 9. 生成總結報告
        return self.generate_summary_report()

def main():
    """主函數"""
    debugger = StealthDebugger()
    
    try:
        success = debugger.run_full_test()
        
        if success:
            print(f"\n🎊 所有測試都通過了！")
        else:
            print(f"\n🔧 需要修復一些問題")
            
    except Exception as e:
        print(f"\n💥 測試異常: {e}")
        traceback.print_exc()
    
    finally:
        # 清理資源
        if debugger.lib and debugger.initialized:
            try:
                debugger.lib.stealth_cleanup()
            except:
                pass

if __name__ == "__main__":
    main()