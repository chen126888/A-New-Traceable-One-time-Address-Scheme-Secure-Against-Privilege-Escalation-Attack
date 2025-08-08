"""
Scheme Management Routes Module
處理方案選擇和切換的路由
"""

from flask import Blueprint, request, jsonify

# 創建方案管理藍圖
schemes_bp = Blueprint('schemes', __name__)

def init_schemes_routes(scheme_manager, demo_state):
    """初始化方案路由，注入依賴"""
    
    @schemes_bp.route('/schemes', methods=['GET'])
    def get_schemes():
        """獲取可用的方案"""
        try:
            available_schemes = scheme_manager.get_available_schemes()
            current_scheme = scheme_manager.get_current_scheme()
            
            # 如果沒有當前方案，預設選擇my_stealth
            if not current_scheme:
                try:
                    my_stealth_available = any(s['id'] == 'my_stealth' and s['available'] for s in available_schemes)
                    if my_stealth_available:
                        result = scheme_manager.switch_scheme('my_stealth')
                        demo_state['current_scheme'] = 'my_stealth' 
                        demo_state['initialized'] = False
                        current_scheme = scheme_manager.get_current_scheme()
                        print(f"Auto-selected default scheme: my_stealth")
                except Exception as e:
                    print(f"Failed to select default scheme: {e}")
            
            return jsonify({
                'schemes': available_schemes,
                'current': current_scheme
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @schemes_bp.route('/schemes/<scheme_id>', methods=['POST'])
    def switch_scheme(scheme_id):
        """切換到不同的方案"""
        try:
            result = scheme_manager.switch_scheme(scheme_id)
            demo_state['current_scheme'] = scheme_id
            demo_state['initialized'] = False  # 重置初始化狀態
            
            # 清除舊的方案數據
            demo_state.pop('keys', None)
            demo_state.pop('addresses', None)
            demo_state.pop('param_file', None)
            
            return jsonify({
                'status': 'success',
                'scheme': result,
                'message': f'Switched to {result["name"]} scheme'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return schemes_bp