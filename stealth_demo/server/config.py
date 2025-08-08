"""
Application Configuration Module
應用配置和常量設置
"""

import os

class Config:
    """應用配置類"""
    
    # 基本設置
    DEBUG = True
    PORT = 3000  # 避免與Vite開發服務器(5173)和其他服務衝突
    HOST = '127.0.0.1'
    
    # 路徑設置
    LIB_DIRECTORY = "lib"
    PARAM_DIRECTORY = "param"
    PBC_PARAM_DIRECTORY = "param/pbc_params"
    ECC_PARAM_DIRECTORY = "param/ecc_params"
    FRONTEND_DIST = "frontend-react/dist"
    
    # 緩衝區設置
    DEFAULT_BUFFER_SIZE = 96  # 所有方案的最大緩衝區大小
    
    # 支援的參數文件類型
    PARAM_FILE_TYPES = {
        'pbc': {
            'directory': PBC_PARAM_DIRECTORY,
            'pattern': '*.param',
            'description': 'PBC Pairing Parameter Files'
        },
        'ecc': {
            'directory': ECC_PARAM_DIRECTORY, 
            'pattern': '*.conf',
            'description': 'Elliptic Curve Parameter Files'
        }
    }
    
    @staticmethod
    def get_param_config(param_type):
        """獲取參數文件配置"""
        return Config.PARAM_FILE_TYPES.get(param_type)
    
    @staticmethod
    def validate_paths():
        """驗證必要的路徑是否存在"""
        required_dirs = [
            Config.LIB_DIRECTORY,
            Config.PARAM_DIRECTORY,
            Config.PBC_PARAM_DIRECTORY,
            Config.ECC_PARAM_DIRECTORY
        ]
        
        missing_dirs = []
        for directory in required_dirs:
            if not os.path.exists(directory):
                missing_dirs.append(directory)
        
        if missing_dirs:
            raise FileNotFoundError(f"Missing required directories: {missing_dirs}")
        
        return True

class DemoState:
    """演示狀態管理類"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """重置所有狀態"""
        self._state = {
            'current_scheme': None,
            'initialized': False,
            'param_file': None,
            'keys': [],
            'addresses': [],
            'dsk_list': [],
            'signatures': []
        }
    
    def get(self, key, default=None):
        """獲取狀態值"""
        return self._state.get(key, default)
    
    def set(self, key, value):
        """設置狀態值"""
        self._state[key] = value
    
    def update(self, updates):
        """批量更新狀態"""
        self._state.update(updates)
    
    def clear(self):
        """清除狀態"""
        self.reset()
    
    def __getitem__(self, key):
        return self._state[key]
    
    def __setitem__(self, key, value):
        self._state[key] = value
    
    def __contains__(self, key):
        return key in self._state
    
    def pop(self, key, default=None):
        """移除並返回狀態值"""
        return self._state.pop(key, default)