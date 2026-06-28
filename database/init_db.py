"""
Database Initialization Module.
Creates all required tables for the Resume Screening System.

WHY THIS FILE IS REQUIRED:
- Creates database schema on application startup
- Ensures all tables exist before the app runs
- Provides a clean way to reset the database

WHAT THIS FILE DOES:
- Creates SQLite database connection
- Defines and creates all tables (users, resumes, jobs, ats_scores, suggestions)
- Handles database creation errors

DATABASE SCHEMA:

1. users: Stores user account information
   - id (Primary Key)
   - username (Unique)
   - email (Unique)
   - password (Hashed)
   - created_at

2. resumes: Stores uploaded resume information
   - id (Primary Key)
   - user_id (Foreign Key to users)
   - filename
   - original_filename
   - extracted_text
   - candidate_name
   - email
   - phone
   - skills (JSON)
   - education
   - experience
   - certifications
   - projects
   - upload_date

3. jobs: Stores job descriptions for matching
   - id (Primary Key)
   - title
   - description
   - required_skills (JSON)
   - created_at

4. ats_scores: Stores ATS calculation results
   - id (Primary Key)
   - resume_id (Foreign Key to resumes)
   - job_id (Foreign Key to jobs)
   - skill_match_score
   - keyword_match_score
   - relevance_score
   - overall_ats_score
   - calculation_date

5. suggestions: Stores improvement suggestions
   - id (Primary Key)
   - resume_id (Foreign Key to resumes)
   - suggestion_type
   - suggestion_text
   - priority
   - created_at

IMPORTANT CONCEPTS:
1. Primary Keys: Unique identifier for each row
2. Foreign Keys: Links between tables, ensures referential integrity
3. TEXT vs VARCHAR: SQLite uses TEXT for all string storage
4. DATETIME: Stores timestamp for record tracking

INTERVIEW PREPARATION:

Q: Why use foreign keys?
A: Foreign keys establish relationships between tables and ensure
   referential integrity - you can't delete a user who has resumes.

Q: What is normalization?
A: Organizing data to reduce redundancy and improve integrity.
   We separate data into logical tables (users, resumes, jobs).

Q: Why store skills as JSON?
A: Skills are a list/array. JSON allows flexible storage without
   creating a separate skills table, keeping it simple for this project.
"""

import sqlite3
import os
from datetime import datetime


def get_db_connection(db_path):
    """
    Create a database connection.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        sqlite3.Connection object
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """
    Initialize the database by creating all required tables.
    This function is called on application startup.

    Creates tables only if they don't exist (IF NOT EXISTS).
    """
    from config import DATABASE_PATH

    # Ensure database directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    conn = get_db_connection(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create resumes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                extracted_text TEXT,
                candidate_name TEXT,
                email TEXT,
                phone TEXT,
                skills TEXT,
                education TEXT,
                experience TEXT,
                certifications TEXT,
                projects TEXT,
                upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Create jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                required_skills TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create ats_scores table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ats_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                job_id INTEGER,
                skill_match_score REAL DEFAULT 0,
                keyword_match_score REAL DEFAULT 0,
                relevance_score REAL DEFAULT 0,
                overall_ats_score REAL DEFAULT 0,
                calculation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resumes (id),
                FOREIGN KEY (job_id) REFERENCES jobs (id)
            )
        ''')

        # Create suggestions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                suggestion_type TEXT,
                suggestion_text TEXT NOT NULL,
                priority INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resumes (id)
            )
        ''')



        conn.commit()
        print("Database initialized successfully!")

    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':
    # Run database initialization directly for testing
    from config import DATABASE_PATH
    init_database()
    print(f"Database created at: {DATABASE_PATH}")
