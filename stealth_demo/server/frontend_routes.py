"""
Frontend Routes Module
處理前端靜態文件服務
"""

from flask import Blueprint, send_from_directory
from config import Config
import os

# 創建前端藍圖
frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def serve_frontend():
    """服務React前端主頁"""
    try:
        return send_from_directory(Config.FRONTEND_DIST, "index.html")
    except FileNotFoundError:
        return """
        <h1>Frontend Not Built</h1>
        <p>Please build the React frontend first:</p>
        <pre>cd frontend-react && npm run build</pre>
        """, 404

@frontend_bp.route('/<path:path>')
def serve_static(path):
    """服務靜態文件"""
    try:
        return send_from_directory(Config.FRONTEND_DIST, path)
    except FileNotFoundError:
        # 對於SPA路由，返回index.html
        try:
            return send_from_directory(Config.FRONTEND_DIST, "index.html")
        except FileNotFoundError:
            return """
            <h1>File Not Found</h1>
            <p>Frontend files are not available. Please build the React frontend:</p>
            <pre>cd frontend-react && npm run build</pre>
            """, 404