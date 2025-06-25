from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from app.config import Config

migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化擴展
    CORS(app)
    migrate.init_app(app)
    
    # 註冊藍圖
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 主頁路由
    @app.route('/')
    def index():
        return "Stealth Transaction System API"
    
    return app
