"""
Application Factory Module
Flask應用工廠，負責創建和配置應用
"""

from flask import Flask
from flask_cors import CORS
from config import Config, DemoState
from scheme_manager import SchemeManager
from api.routes import init_routes
from api.schemes import init_schemes_routes
from frontend_routes import frontend_bp
import os

def create_app():
    """創建並配置Flask應用"""
    
    # 驗證路徑
    try:
        Config.validate_paths()
        print("✅ All required paths validated")
    except FileNotFoundError as e:
        print(f"❌ Path validation failed: {e}")
        print("💡 Make sure you're running from the project root directory")
        exit(1)
    
    # 初始化方案管理器
    try:
        scheme_manager = SchemeManager(lib_directory=Config.LIB_DIRECTORY)
        print("✅ Scheme Manager initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Scheme Manager: {e}")
        exit(1)
    
    # 創建應用
    app = Flask(__name__, static_folder=Config.FRONTEND_DIST)
    app.config.from_object(Config)
    
    # 啟用CORS
    CORS(app)
    
    # 初始化演示狀態
    demo_state = DemoState()
    
    # 註冊藍圖
    register_blueprints(app, scheme_manager, demo_state)
    
    # 添加錯誤處理
    register_error_handlers(app)
    
    return app, scheme_manager, demo_state

def register_blueprints(app, scheme_manager, demo_state):
    """註冊所有藍圖"""
    
    # 註冊API路由
    api_bp = init_routes(scheme_manager, demo_state)
    app.register_blueprint(api_bp)
    
    # 註冊方案管理路由
    schemes_bp = init_schemes_routes(scheme_manager, demo_state)
    app.register_blueprint(schemes_bp)
    
    # 註冊前端路由
    app.register_blueprint(frontend_bp)
    
    print("✅ All blueprints registered")

def register_error_handlers(app):
    """註冊錯誤處理器"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        # 記錄錯誤但不暴露內部信息
        app.logger.error(f"Unhandled exception: {e}")
        return {'error': 'An unexpected error occurred'}, 500

def print_startup_info(scheme_manager):
    """打印啟動信息"""
    print("\n🚀 Starting Multi-Scheme Demo Server...")
    print("=" * 50)
    print("📊 Available schemes:")
    
    schemes = scheme_manager.get_available_schemes()
    for scheme in schemes:
        status = "✅ Available" if scheme['available'] else "❌ Not Available"
        functions_count = len(scheme['functions'])
        param_type = scheme['param_type'].upper()
        
        print(f"   • {scheme['id']}: {scheme['name']}")
        print(f"     Status: {status}")
        print(f"     Type: {param_type} | Functions: {functions_count}")
        
        if not scheme['available']:
            print(f"     Library: {scheme.get('lib_path', 'N/A')}")
    
    print("=" * 50)
    print(f"🌐 Server will start on http://{Config.HOST}:{Config.PORT}")
    print("💡 Make sure to build frontend first: cd frontend-react && npm run build")
    print("=" * 50)