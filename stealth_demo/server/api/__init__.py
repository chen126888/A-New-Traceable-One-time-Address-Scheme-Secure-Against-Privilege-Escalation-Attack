"""
API Module
包含所有API相關的路由和處理器
"""

from .routes import init_routes
from .schemes import init_schemes_routes

__all__ = ['init_routes', 'init_schemes_routes']