import os

# Base directory of the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Secret key for session management and CSRF protection
# In production, use environment variable
SECRET_KEY = os.environ.get('SECRET_KEY') or 'resume-screening-secret-key-2024'

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'database.db')
DATABASE_URI = f'sqlite:///{DATABASE_PATH}'

# Upload configuration
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# NLP Configuration
# spaCy model for English language
SPACY_MODEL = 'en_core_web_sm'

# NLTK data download path
NLTK_DATA_PATH = os.path.join(BASE_DIR, 'nltk_data')

# ATS Scoring weights
SKILL_WEIGHT = 0.4
KEYWORD_WEIGHT = 0.3
RELEVANCE_WEIGHT = 0.3

# Session configuration
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour in seconds
