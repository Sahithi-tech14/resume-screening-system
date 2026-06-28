"""
Authentication Routes - Handles user login, registration, and logout.

WHY THIS FILE IS REQUIRED:
- Provides user authentication functionality
- Handles form validation and error handling
- Implements secure session management

WHAT THIS FILE DOES:
- Login: Verifies credentials and creates session
- Register: Creates new user accounts with hashed passwords
- Logout: Ends user session

HOW IT CONNECTS TO OTHER FILES:
- Uses User model for database operations
- Uses Flask-Login for session management
- Renders login.html and register.html templates

IMPORTANT CONCEPTS:
1. Blueprint: Modular routing in Flask
2. Flask-Login: User session management
3. Flash messages: One-time notifications
4. Form validation: Checking user input

INTERVIEW PREPARATION:

Q: Why use Flask-Login instead of implementing sessions manually?
A: Flask-Login provides secure session management, remember me cookies,
   and protects against session fixation attacks.

Q: What are flash messages?
A: Flash messages are stored in the session and displayed once on the
   next request. They're used for notifications like success/error messages.

Q: Why check if user already exists during registration?
A: To prevent duplicate accounts and provide meaningful error messages
   to users instead of database errors.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User

# Create authentication blueprint
auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.

    GET: Display login form
    POST: Process login credentials

    Returns:
        Redirect to dashboard on success, login form otherwise
    """
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember = request.form.get('remember', False)

        # Validate input
        if not username or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('login.html')

        # Find user by username
        user = User.get_by_username(username)

        # Check if user exists and password is correct
        if user is None or not user.verify_password(password):
            flash('Invalid username or password.', 'error')
            return render_template('login.html')

        # Log the user in
        login_user(user, remember=remember)

        flash(f'Welcome back, {user.username}!', 'success')

        # Redirect to next page or dashboard
        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard.home'))

    return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.

    GET: Display registration form
    POST: Create new user account

    Returns:
        Redirect to login on success, registration form otherwise
    """
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Validate input
        errors = []

        if not username or not email or not password or not confirm_password:
            errors.append('Please fill in all fields.')

        if len(username) < 3:
            errors.append('Username must be at least 3 characters.')

        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')

        if password != confirm_password:
            errors.append('Passwords do not match.')

        if '@' not in email or '.' not in email:
            errors.append('Please enter a valid email address.')

        # Check if username or email already exists
        if User.get_by_username(username):
            errors.append('Username already exists.')

        if User.get_by_email(email):
            errors.append('Email already registered.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')

        # Create new user
        user = User.create(username, email, password)

        if user:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')

    return render_template('register.html')


@auth.route('/logout')
@login_required
def logout():
    """
    Handle user logout.
    Requires user to be logged in.

    Returns:
        Redirect to login page
    """
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
