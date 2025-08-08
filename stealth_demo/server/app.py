"""
Main application file for the stealth demo server.
Refactored version with modular architecture.
"""
from flask import Flask, send_from_directory
import traceback
from flask import jsonify

from config import config
from library_wrapper import stealth_lib
from routes import setup_routes


def create_app():
    """Create and configure the Flask application."""
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
    
    # Setup all API routes
    setup_routes(app)
    
    return app


def main():
    """Main function to run the application."""
    app = create_app()
    
    print("🚀 Starting Interactive Stealth Demo Server")
    print("🎯 Features: Selectable inputs for all operations")
    print("💡 New: DSK generation, parameter file selection, flexible verification")
    print("🌐 Server will run on http://localhost:5000")
    print(f"📦 DSK functions available: {stealth_lib.dsk_functions_available}")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        if config.system_initialized:
            stealth_lib.cleanup()
            print("🧹 Library cleanup completed")


if __name__ == "__main__":
    main()