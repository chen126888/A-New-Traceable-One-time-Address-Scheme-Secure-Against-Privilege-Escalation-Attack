"""
API Routes Module
處理所有的API端點路由
"""

from flask import Blueprint, request, jsonify
import os
import glob
import traceback
from ctypes import create_string_buffer

# 創建API藍圖
api = Blueprint('api', __name__, url_prefix='/api')

def init_routes(scheme_manager, demo_state):
    """初始化路由，注入依賴"""
    
    @api.route('/status', methods=['GET'])
    def get_status():
        """獲取當前系統狀態"""
        try:
            current_scheme = scheme_manager.get_current_scheme()
            return jsonify({
                'current_scheme': current_scheme,
                'initialized': demo_state['initialized'],
                'param_file': demo_state['param_file']
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @api.route('/param_files', methods=['GET'])
    def get_param_files():
        """根據當前方案獲取可用的參數文件"""
        try:
            current_scheme = scheme_manager.get_current_scheme()
            if not current_scheme:
                return jsonify({'error': 'No scheme selected'}), 400
                
            param_type = current_scheme['param_type']
            
            if param_type == 'pbc':
                param_dir = "param/pbc_params"
                pattern = "*.param"
                description = "PBC Pairing Parameter Files"
            elif param_type == 'ecc':
                param_dir = "param/ecc_params"
                pattern = "*.conf"
                description = "Elliptic Curve Parameter Files"
            else:
                return jsonify({'error': f'Unknown parameter type: {param_type}'}), 400
                
            param_files = glob.glob(os.path.join(param_dir, pattern))
            param_files = [os.path.basename(f) for f in param_files]
            
            return jsonify({
                'param_files': param_files,
                'param_type': param_type,
                'description': description,
                'directory': param_dir
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @api.route('/setup', methods=['POST'])
    def setup_system():
        """使用選定的參數文件初始化系統"""
        try:
            data = request.get_json()
            param_file = data.get('param_file')
            
            if not param_file:
                return jsonify({'error': 'Parameter file required'}), 400
                
            current_scheme = scheme_manager.get_current_scheme()
            if not current_scheme:
                return jsonify({'error': 'No scheme selected'}), 400
                
            # 確定參數文件路徑
            param_type = current_scheme['param_type']
            if param_type == 'pbc':
                param_path = f"param/pbc_params/{param_file}"
            elif param_type == 'ecc':
                param_path = f"param/ecc_params/{param_file}"
            else:
                return jsonify({'error': f'Unknown parameter type: {param_type}'}), 400
                
            if not os.path.exists(param_path):
                return jsonify({'error': f'Parameter file not found: {param_path}'}), 400
                
            # 初始化方案
            lib = scheme_manager.get_lib()
            prefix = scheme_manager.get_function_prefix()
            
            init_func = getattr(lib, f"{prefix}init")
            result = init_func(param_path.encode('utf-8'))
            
            if result == 0:  # 成功
                demo_state['initialized'] = True
                demo_state['param_file'] = param_file
                scheme_manager.mark_initialized()
                
                # 準備回傳數據
                response_data = {
                    'status': 'success',
                    'message': f'System initialized with {param_file}',
                    'scheme': current_scheme['name'],
                    'param_type': param_type
                }
                
                # 如果是my_stealth方案，生成trace key
                if current_scheme['id'] == 'my_stealth' and scheme_manager.is_function_available('tracekeygen'):
                    try:
                        print("Attempting to generate trace key for my_stealth...")
                        
                        # 先檢查初始化狀態
                        is_init_func = getattr(lib, f"{prefix}is_initialized", None)
                        if is_init_func and is_init_func() == 0:
                            print("Error: Library not initialized for tracekeygen")
                        else:
                            print("Library is initialized, calling tracekeygen...")
                            buffer_size = 96
                            tk_buf = create_string_buffer(buffer_size)
                            k_buf = create_string_buffer(buffer_size)
                            
                            tracekeygen_func = getattr(lib, f"{prefix}tracekeygen_simple")
                            tracekeygen_func(tk_buf, k_buf, buffer_size)
                            
                            print("Tracekeygen completed, getting element sizes...")
                            
                            # 獲取元素大小信息
                            g1_size = 0
                            zr_size = 0
                            try:
                                g1_size_func = getattr(lib, f"{prefix}element_size_G1", None)
                                zr_size_func = getattr(lib, f"{prefix}element_size_Zr", None)
                                if g1_size_func and zr_size_func:
                                    g1_size = g1_size_func()
                                    zr_size = zr_size_func()
                                    print(f"Element sizes - G1: {g1_size}, Zr: {zr_size}")
                            except AttributeError as e:
                                print(f"Could not get element sizes: {e}")
                            
                            response_data.update({
                                'TK_hex': tk_buf.raw.hex(),
                                'k_hex': k_buf.raw.hex(),
                                'g1_size': g1_size,
                                'zr_size': zr_size
                            })
                            print("Trace key data added to response")
                            
                    except Exception as e:
                        print(f"Trace key generation failed: {e}")
                        import traceback
                        traceback.print_exc()
                        # 即使trace key生成失敗，系統初始化仍然成功
                else:
                    print(f"Scheme {current_scheme['id']} does not support tracekeygen")
                
                return jsonify(response_data)
            else:
                return jsonify({'error': 'Initialization failed'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @api.route('/keygen', methods=['GET'])
    def generate_key():
        """生成新的密鑰對"""
        try:
            if not demo_state['initialized']:
                return jsonify({'error': 'System not initialized'}), 400
                
            current_scheme = scheme_manager.get_current_scheme()
            if not scheme_manager.is_function_available('keygen'):
                return jsonify({'error': 'Key generation not supported by current scheme'}), 400
                
            lib = scheme_manager.get_lib()
            prefix = scheme_manager.get_function_prefix()
            
            # 使用方案特定的函數生成密鑰
            key_index = len(demo_state.get('keys', []))
            buffer_size = 96  # 所有方案的最大緩衝區大小
            keygen_func = getattr(lib, f"{prefix}keygen_simple")
            
            # 根據不同scheme調用不同的keygen函數
            if current_scheme['id'] in ['my_stealth', 'cryptonote2']:
                # my_stealth和cryptonote2需要4個輸出緩衝區: A, B, a, b
                A_buf = create_string_buffer(buffer_size)  # public key A
                B_buf = create_string_buffer(buffer_size)  # public key B  
                a_buf = create_string_buffer(buffer_size)  # private key a
                b_buf = create_string_buffer(buffer_size)  # private key b
                
                keygen_func(A_buf, B_buf, a_buf, b_buf, buffer_size)
                
                key_data = {
                    'id': f"{current_scheme['id']}_key_{key_index}",
                    'A_hex': A_buf.raw.hex(),
                    'B_hex': B_buf.raw.hex(), 
                    'a_hex': a_buf.raw.hex(),
                    'b_hex': b_buf.raw.hex(),
                    'public_key': A_buf.raw.hex(),  # 兼容性：主要公鑰
                    'private_key': a_buf.raw.hex(), # 兼容性：主要私鑰
                    'scheme': current_scheme['id'],
                    'index': key_index
                }
                
            elif current_scheme['id'] in ['zhao', 'hdwsa', 'sitaiba']:
                # zhao、hdwsa、sitaiba只需要2個輸出緩衝區: public_key, private_key
                public_key_buf = create_string_buffer(buffer_size)
                private_key_buf = create_string_buffer(buffer_size)
                
                keygen_func(public_key_buf, private_key_buf, buffer_size)
                
                key_data = {
                    'id': f"{current_scheme['id']}_key_{key_index}",
                    'public_key': public_key_buf.raw.hex(),
                    'private_key': private_key_buf.raw.hex(),
                    'A_hex': public_key_buf.raw.hex(),  # 兼容性
                    'scheme': current_scheme['id'],
                    'index': key_index
                }
            else:
                return jsonify({'error': f'Unknown scheme for keygen: {current_scheme["id"]}'}), 400
            
            # 存儲密鑰
            if 'keys' not in demo_state:
                demo_state['keys'] = []
            demo_state['keys'].append(key_data)
            
            return jsonify({
                'status': 'success',
                'key': key_data
            })
            
        except Exception as e:
            print(f"Key generation error: {e}")
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    @api.route('/keylist', methods=['GET'])
    def get_key_list():
        """獲取生成的密鑰列表"""
        return jsonify(demo_state.get('keys', []))

    @api.route('/addresslist', methods=['GET'])
    def get_address_list():
        """獲取地址列表"""
        return jsonify(demo_state.get('addresses', []))

    @api.route('/dsklist', methods=['GET'])
    def get_dsk_list():
        """獲取DSK列表"""
        return jsonify(demo_state.get('dsk_list', []))

    @api.route('/tx_messages', methods=['GET'])
    def get_tx_messages():
        """獲取交易消息列表"""
        return jsonify(demo_state.get('tx_messages', []))
    
    @api.route('/signatures', methods=['GET'])
    def get_signatures():
        """獲取簽名列表"""
        return jsonify(demo_state.get('signatures', []))

    @api.route('/reset', methods=['POST'])
    def reset_system():
        """重置所有演示數據"""
        try:
            # 清除演示狀態
            demo_state.clear()
            demo_state.update({
                'current_scheme': None,
                'initialized': False,
                'param_file': None
            })
            
            return jsonify({'status': 'success', 'message': 'System reset'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return api