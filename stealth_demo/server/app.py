"""
Main application file for the stealth demo server.
Refactored version with modular architecture.
"""
from flask import Flask, send_from_directory
import traceback
from flask import jsonify

from multi_scheme_config import config
from scheme_manager import scheme_manager
# from library_wrapper import stealth_lib  # TODO: Will be managed by scheme_manager
from unified_routes import setup_routes


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder="../frontend")
    
    # Add simple CORS headers manually
    @app.after_request
    def after_request(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    # Handle OPTIONS requests for CORS preflight
    @app.route('/<path:path>', methods=['OPTIONS'])
    def options_handler(path):
        return '', 200
    
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
    import os
    
    app = create_app()
    
    # Only print startup message in main process (not in Flask reloader)
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        print("🚀 Starting Multi-Scheme Cryptographic Demo Server")
        print("🎯 Features: Multiple scheme support, selectable inputs for all operations")
        print("💡 Schemes: Stealth (complete), Sitaiba (placeholder)")
        print("🌐 Server will run on http://localhost:5001")
        print(f"📦 Available schemes: {scheme_manager.get_available_schemes()}")
        print(f"🔧 Current scheme: {scheme_manager.get_current_scheme_name()}")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        # if config.system_initialized:
        #     stealth_lib.cleanup()
        #     print("🧹 Library cleanup completed")
        # TODO: Will be managed by scheme_manager


if __name__ == "__main__":
    main()