"""
Main Flask Application Entry Point.
This is the core file that initializes and runs the Flask application.

WHY THIS FILE IS REQUIRED:
- Entry point for the entire application
- Configures Flask, database, and Flask-Login
- Registers all blueprints/routes
- Creates necessary directories and initializes database

WHAT THIS FILE DOES:
- Creates Flask app instance
- Configures database connection
- Sets up user authentication with Flask-Login
- Registers route blueprints (auth, resume, dashboard)
- Initializes database tables on startup
- Runs the development server

HOW IT CONNECTS TO OTHER FILES:
- Imports config from config.py
- Imports database initialization from database/init_db.py
- Imports User model for Flask-Login
- Registers blueprints from routes/ directory

IMPORTANT CONCEPTS:
1. Flask Application Factory Pattern
2. Blueprint for modular routing
3. Flask-Login for session management
4. SQLite database initialization

INTERVIEW PREPARATION:

Q: What is the Flask Application Factory Pattern?
A: It's a design pattern where we create Flask app instances
   inside a function. This allows multiple instances for testing
   and better configuration management.

Q: Why use Blueprints?
A: Blueprints allow us to organize routes into modules, making
   the code more maintainable and easier to understand.

Q: How does Flask-Login work?
A: Flask-Login manages user sessions, provides decorators like
   @login_required, and handles remember me functionality.
"""

import os
from flask import Flask
from flask_login import LoginManager
from config import SECRET_KEY, DATABASE_PATH, UPLOAD_FOLDER
from database.init_db import init_database
from models.user import User

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'


def create_app():
    """
    Application Factory Pattern - Creates and configures the Flask app.

    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DATABASE_PATH'] = DATABASE_PATH
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # Ensure upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    # Initialize database
    init_database()

    # Initialize Flask-Login
    login_manager.init_app(app)

    # Register blueprints
    from routes.auth import auth
    from routes.resume_routes import resume_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(resume_bp, url_prefix='/resume')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    # Main route
    @app.route('/')
    def index():
        """Redirect to login or dashboard based on auth status."""
        from flask import redirect, url_for
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.home'))
        return redirect(url_for('auth.login'))

    return app


@login_manager.user_loader
def load_user(user_id):
    """
    Callback function for Flask-Login to load a user from the database.

    Args:
        user_id: The user ID stored in the session

    Returns:
        User object or None if not found
    """
    return User.get_by_id(int(user_id))


# Create application instance
app = create_app()


if __name__ == '__main__':
    """
    Run the development server.

    NOTE: debug=True should be False in production for security.
    """
    print("=" * 50)
    print("AI-Powered Resume Screening System")
    print("Starting development server...")
    print("=" * 50)
    print("\nAccess the application at: http://127.0.0.1:5000")
    print("\nPress Ctrl+C to stop the server\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
