"""
Stealth Demo Server Package

A modular Flask application for stealth cryptographic operations.
Provides key generation, address management, signing, verification, and identity tracing.
"""

__version__ = "1.0.0"
__author__ = "Stealth Demo Team"

from .app import create_app, main

__all__ = [
    'create_app',
    'main',
]
