#!/usr/bin/env python3

import sys
sys.path.append('/mnt/c/Users/chen1/Desktop/master/thesis/nccu/new/code/stealth_demo/server')

from schemes.scheme_manager import scheme_manager
from schemes.sitaiba_scheme import SitaibaScheme

def main():
    print("🔍 簡化測試：檢查 verify_address 和 trace_identity 的數據")
    print("=" * 60)
    
    # 註冊和啟動 scheme
    scheme_manager.register_scheme(SitaibaScheme)
    scheme_manager.activate_scheme("sitaiba")
    
    # Setup
    setup_result = scheme_manager.setup_system(param_file="a.param")
    tracer_key = setup_result.get('tracer_A_hex', '')
    print(f"1. Setup complete, tracer key: {tracer_key[:20]}...")
    
    # 生成 key
    key_result = scheme_manager.generate_keypair(num_keys=1)
    key_data = key_result
    A_hex = key_data['A_hex']
    B_hex = key_data['B_hex']
    a_hex = key_data['a_hex']
    
    print(f"2. Key generated:")
    print(f"   A: {A_hex[:20]}...")
    print(f"   B: {B_hex[:20]}...")
    print(f"   a: {a_hex}")
    
    # 生成地址
    addr_result = scheme_manager.generate_address(key_index=0, num_addresses=1)
    addr_data = addr_result
    addr_hex = addr_data['addr_hex']
    r1_hex = addr_data['r1_hex']
    r2_hex = addr_data['r2_hex']
    
    print(f"3. Address generated:")
    print(f"   Addr: {addr_hex[:20]}...")
    print(f"   R1:   {r1_hex[:20]}...")
    print(f"   R2:   {r2_hex[:20]}...")
    
    # 檢查數據長度
    print(f"4. Data lengths:")
    print(f"   A_hex: {len(A_hex)} chars")
    print(f"   B_hex: {len(B_hex)} chars")  
    print(f"   a_hex: {len(a_hex)} chars")
    print(f"   addr_hex: {len(addr_hex)} chars")
    print(f"   r1_hex: {len(r1_hex)} chars")
    print(f"   r2_hex: {len(r2_hex)} chars")
    
    # 驗證地址 - 這是問題所在
    print(f"5. Testing address verification...")
    verify_result = scheme_manager.verify_address(address_index=0, key_index=0)
    print(f"   Verification result: {verify_result['valid']}")
    print(f"   Status: {verify_result['status']}")
    
    # 追蹤身份 - 這也是問題所在  
    print(f"6. Testing identity tracing...")
    trace_result = scheme_manager.trace_identity(address_index=0)
    recovered_b = trace_result['recovered_b_hex']
    original_b = trace_result['original_owner']['B_hex']
    
    print(f"   Original  B: {original_b[:20]}...")
    print(f"   Recovered B: {recovered_b[:20]}...")
    print(f"   Perfect match: {trace_result['perfect_match']}")
    print(f"   Are they equal? {original_b == recovered_b}")
    
    # 比較前20個字符
    if len(original_b) >= 20 and len(recovered_b) >= 20:
        print(f"   First 20 chars match: {original_b[:20] == recovered_b[:20]}")
        print(f"   First 40 chars match: {original_b[:40] == recovered_b[:40] if len(original_b) >= 40 and len(recovered_b) >= 40 else 'N/A'}")

if __name__ == "__main__":
    main()