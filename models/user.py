import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from database.init_db import get_db_connection
from config import DATABASE_PATH


class User(UserMixin):
    """
    User class for authentication and account management.
    Inherits from UserMixin to provide Flask-Login compatibility.
    """

    def __init__(self, id, username, email, password, created_at):
        """
        Initialize a User instance.

        Args:
            id: User's unique identifier
            username: User's display name
            email: User's email address
            password: User's hashed password
            created_at: Account creation timestamp
        """
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.created_at = created_at

    @staticmethod
    def get_by_id(user_id):
        """
        Retrieve a user by their ID.

        Args:
            user_id: The user's ID

        Returns:
            User object if found, None otherwise
        """
        conn = get_db_connection(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                password=row['password'],
                created_at=row['created_at']
            )
        return None

    @staticmethod
    def get_by_username(username):
        """
        Retrieve a user by their username.

        Args:
            username: The username to search for

        Returns:
            User object if found, None otherwise
        """
        conn = get_db_connection(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                password=row['password'],
                created_at=row['created_at']
            )
        return None

    @staticmethod
    def get_by_email(email):
        """
        Retrieve a user by their email.

        Args:
            email: The email to search for

        Returns:
            User object if found, None otherwise
        """
        conn = get_db_connection(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                password=row['password'],
                created_at=row['created_at']
            )
        return None

    @staticmethod
    def create(username, email, password):
        """
        Create a new user account.

        Args:
            username: Desired username
            email: User's email
            password: Plain text password (will be hashed)

        Returns:
            User object if successful, None if user exists
        """
        # Check if username or email already exists
        if User.get_by_username(username) or User.get_by_email(email):
            return None

        # Hash the password before storing
        hashed_password = generate_password_hash(password)

        conn = get_db_connection(DATABASE_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, hashed_password)
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()

            return User.get_by_id(user_id)

        except sqlite3.Error:
            conn.rollback()
            conn.close()
            return None

    def verify_password(self, password):
        """
        Verify if the provided password matches the stored hash.

        Args:
            password: Plain text password to verify

        Returns:
            True if password matches, False otherwise
        """
        return check_password_hash(self.password, password)

    def __repr__(self):
        """String representation of User object."""
        return f'<User {self.username}>'
