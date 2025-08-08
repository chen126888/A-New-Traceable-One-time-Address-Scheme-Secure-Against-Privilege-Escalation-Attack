"""
Stealth Demo Server Package

A modular Flask application for stealth cryptographic operations.
Provides key generation, address management, signing, verification, and identity tracing.
"""

__version__ = "1.0.0"
__author__ = "Stealth Demo Team"

from .app_refactored import create_app, main
from .config import config
from .crypto_services import CryptoServices
from .library_wrapper import stealth_lib

__all__ = [
    'create_app',
    'main', 
    'config',
    'CryptoServices',
    'stealth_lib'
]