"""
Multi-Scheme Cryptographic Demo Server
主應用入口點

啟動方式:
    python3 server/app.py

要求:
    - 從項目根目錄運行
    - 前端已構建: cd frontend-react && npm run build
    - 所有方案庫已編譯: make all
"""

from app_factory import create_app, print_startup_info
from config import Config
import sys
import os

def main():
    """主函數"""
    
    # 智能路徑檢測 - 支援從項目根目錄或server目錄運行
    current_dir = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 如果在server目錄內運行，切換到父目錄
    if os.path.basename(current_dir) == 'server':
        project_root = os.path.dirname(current_dir)
        os.chdir(project_root)
        print(f"🔄 Auto-switched to project root: {project_root}")
    
    # 檢查必要的目錄是否存在
    if not os.path.exists('lib') or not os.path.exists('param'):
        print("❌ Error: Required directories not found")
        print(f"🔍 Current directory: {os.getcwd()}")
        print("💡 Make sure you have 'lib' and 'param' directories")
        print("💡 Try: python3 server/app.py (from project root)")
        print("💡   or: python3 app.py (from server folder)")
        sys.exit(1)
    
    try:
        # 創建應用
        app, scheme_manager, demo_state = create_app()
        
        # 打印啟動信息
        print_startup_info(scheme_manager)
        
        # 啟動服務器
        app.run(
            debug=Config.DEBUG,
            host=Config.HOST,
            port=Config.PORT,
            use_reloader=False  # 禁用reloader避免路徑問題
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()