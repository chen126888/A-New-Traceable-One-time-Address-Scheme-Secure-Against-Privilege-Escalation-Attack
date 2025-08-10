"""
Multi-scheme application file for the stealth demo server.
Supports multiple cryptographic schemes with plugin architecture.
"""
from flask import Flask, send_from_directory
import traceback
from flask import jsonify

from multi_scheme_routes import setup_multi_scheme_routes


def create_multi_scheme_app():
    """Create and configure the multi-scheme Flask application."""
    app = Flask(__name__, static_folder="../frontend")
    
    # Setup global error handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Global error handler"""
        error_info = {
            "error": str(e),
            "type": type(e).__name__
        }
        
        if app.debug:
            error_info["traceback"] = traceback.format_exc()
        
        return jsonify(error_info), 500
    
    # Setup static file route
    @app.route("/")
    def index():
        return send_from_directory("../frontend", "index.html")
    
    # Setup all multi-scheme API routes
    setup_multi_scheme_routes(app)
    
    return app


def main():
    """Main function to run the multi-scheme application."""
    app = create_multi_scheme_app()
    
    print("🚀 Starting Multi-Scheme Crypto Demo Server")
    print("🎯 Features: Multiple cryptographic schemes with plugin architecture")
    print("🔧 Capabilities: Dynamic scheme switching, modular operations")
    print("🌐 Server will run on http://localhost:5000")
    print("")
    print("📋 Available API endpoints:")
    print("   GET  /api/schemes - List available schemes")
    print("   POST /api/schemes/activate - Activate a scheme")
    print("   GET  /api/status - Get system status")
    print("   POST /api/setup - Initialize active scheme")
    print("   GET  /api/param_files - Get parameter files")
    print("   ... (operation endpoints based on active scheme capabilities)")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Multi-scheme server stopped")


if __name__ == "__main__":
    main()