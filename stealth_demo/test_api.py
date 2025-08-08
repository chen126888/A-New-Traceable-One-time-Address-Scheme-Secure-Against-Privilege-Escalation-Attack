#!/usr/bin/env python3
"""
测试修复後的API功能
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:3000/api"

def test_api_flow():
    """測試完整的API流程"""
    
    print("🔍 Testing API flow...")
    
    # 1. 获取系统状态
    print("\n1. Getting system status...")
    response = requests.get(f"{BASE_URL}/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # 2. 切换到my_stealth方案
    print("\n2. Switching to my_stealth scheme...")
    response = requests.post(f"{BASE_URL}/schemes/my_stealth/select")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # 3. 获取参数文件
    print("\n3. Getting parameter files...")
    response = requests.get(f"{BASE_URL}/param_files")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {data}")
    
    if not data.get('param_files'):
        print("❌ No parameter files found!")
        return False
    
    param_file = data['param_files'][0]  # 使用第一个参数文件
    print(f"Using parameter file: {param_file}")
    
    # 4. 初始化系统
    print("\n4. Initializing system...")
    response = requests.post(f"{BASE_URL}/setup", json={'param_file': param_file})
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Setup successful!")
        print(f"TK_hex: {data.get('TK_hex', 'N/A')[:20]}...")
        print(f"k_hex: {data.get('k_hex', 'N/A')[:20]}...")
        print(f"G1 size: {data.get('g1_size', 'N/A')}")
        print(f"Zr size: {data.get('zr_size', 'N/A')}")
    else:
        print(f"❌ Setup failed: {response.json()}")
        return False
    
    # 5. 生成密钥
    print("\n5. Generating keys...")
    response = requests.get(f"{BASE_URL}/keygen")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Keygen successful!")
        key = data.get('key', {})
        print(f"A_hex: {key.get('A_hex', 'N/A')[:20]}...")
        print(f"B_hex: {key.get('B_hex', 'N/A')[:20]}...")
    else:
        print(f"❌ Keygen failed: {response.json()}")
        return False
    
    print("\n✅ All tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_api_flow()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server is running on port 3000.")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")