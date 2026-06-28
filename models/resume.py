import sqlite3
import json
from datetime import datetime
from database.init_db import get_db_connection
from config import DATABASE_PATH


class Resume:
    """
    Resume class for managing resume data.
    """

    def __init__(self, id, user_id, filename, original_filename, extracted_text,
                 candidate_name, email, phone, skills, education, experience,
                 certifications, projects, upload_date):
        """
        Initialize a Resume instance.
        """
        self.id = id
        self.user_id = user_id
        self.filename = filename
        self.original_filename = original_filename
        self.extracted_text = extracted_text
        self.candidate_name = candidate_name
        self.email = email
        self.phone = phone
        self.skills = json.loads(skills) if skills else []
        self.education = education
        self.experience = experience
        self.certifications = certifications
        self.projects = projects
        self.upload_date = upload_date

    @staticmethod
    def get_by_id(resume_id):
        """
        Retrieve a resume by its ID.

        Args:
            resume_id: The resume's ID

        Returns:
            Resume object if found, None otherwise
        """
        conn = get_db_connection(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return Resume(
                id=row['id'],
                user_id=row['user_id'],
                filename=row['filename'],
                original_filename=row['original_filename'],
                extracted_text=row['extracted_text'],
                candidate_name=row['candidate_name'],
                email=row['email'],
                phone=row['phone'],
                skills=row['skills'],
                education=row['education'],
                experience=row['experience'],
                certifications=row['certifications'],
                projects=row['projects'],
                upload_date=row['upload_date']
            )
        return None

    @staticmethod
    def get_by_user(user_id):
        """
        Retrieve all resumes for a user.

        Args:
            user_id: The user's ID

        Returns:
            List of Resume objects
        """
        conn = get_db_connection(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM resumes WHERE user_id = ? ORDER BY upload_date DESC',
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        resumes = []
        for row in rows:
            resumes.append(Resume(
                id=row['id'],
                user_id=row['user_id'],
                filename=row['filename'],
                original_filename=row['original_filename'],
                extracted_text=row['extracted_text'],
                candidate_name=row['candidate_name'],
                email=row['email'],
                phone=row['phone'],
                skills=row['skills'],
                education=row['education'],
                experience=row['experience'],
                certifications=row['certifications'],
                projects=row['projects'],
                upload_date=row['upload_date']
            ))
        return resumes

    @staticmethod
    def get_all():
        """
        Retrieve all resumes (for ranking feature).

        Returns:
            List of all Resume objects
        """
        conn = get_db_connection(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM resumes ORDER BY upload_date DESC')
        rows = cursor.fetchall()
        conn.close()

        resumes = []
        for row in rows:
            resumes.append(Resume(
                id=row['id'],
                user_id=row['user_id'],
                filename=row['filename'],
                original_filename=row['original_filename'],
                extracted_text=row['extracted_text'],
                candidate_name=row['candidate_name'],
                email=row['email'],
                phone=row['phone'],
                skills=row['skills'],
                education=row['education'],
                experience=row['experience'],
                certifications=row['certifications'],
                projects=row['projects'],
                upload_date=row['upload_date']
            ))
        return resumes

    @staticmethod
    def create(user_id, filename, original_filename, extracted_text=None):
        """
        Create a new resume record.

        Args:
            user_id: The uploader's user ID
            filename: The stored filename (unique)
            original_filename: Original file name
            extracted_text: Text extracted from the file (optional)

        Returns:
            Resume object if successful, None otherwise
        """
        conn = get_db_connection(DATABASE_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute(
                '''INSERT INTO resumes
                   (user_id, filename, original_filename, extracted_text)
                   VALUES (?, ?, ?, ?)''',
                (user_id, filename, original_filename, extracted_text)
            )
            conn.commit()
            resume_id = cursor.lastrowid
            conn.close()

            return Resume.get_by_id(resume_id)

        except sqlite3.Error:
            conn.rollback()
            conn.close()
            return None

    def update_parsed_data(self, candidate_name=None, email=None, phone=None,
                           skills=None, education=None, experience=None,
                           certifications=None, projects=None):
        """
        Update the parsed resume data after NLP processing.

        Args:
            All parsed fields from resume parser

        Returns:
            True if successful, False otherwise
        """
        conn = get_db_connection(DATABASE_PATH)
        cursor = conn.cursor()

        try:
            skills_json = json.dumps(skills) if skills else None

            cursor.execute(
                '''UPDATE resumes SET
                   candidate_name = ?, email = ?, phone = ?,
                   skills = ?, education = ?, experience = ?,
                   certifications = ?, projects = ?
                   WHERE id = ?''',
                (candidate_name, email, phone, skills_json,
                 education, experience, certifications, projects, self.id)
            )
            conn.commit()
            conn.close()

            # Update instance variables
            self.candidate_name = candidate_name
            self.email = email
            self.phone = phone
            self.skills = skills if skills else []
            self.education = education
            self.experience = experience
            self.certifications = certifications
            self.projects = projects

            return True

        except sqlite3.Error:
            conn.rollback()
            conn.close()
            return False

    def update_extracted_text(self, extracted_text):
        """
        Update the extracted text.

        Args:
            extracted_text: Full text extracted from resume

        Returns:
            True if successful, False otherwise
        """
        conn = get_db_connection(DATABASE_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute(
                'UPDATE resumes SET extracted_text = ? WHERE id = ?',
                (extracted_text, self.id)
            )
            conn.commit()
            conn.close()
            self.extracted_text = extracted_text
            return True

        except sqlite3.Error:
            conn.rollback()
            conn.close()
            return False

    def delete(self):
        """
        Delete the resume record.

        Returns:
            True if successful, False otherwise
        """
        import os
        from config import UPLOAD_FOLDER

        conn = get_db_connection(DATABASE_PATH)
        cursor = conn.cursor()

        try:
            # Delete from database
            cursor.execute('DELETE FROM resumes WHERE id = ?', (self.id,))
            conn.commit()
            conn.close()

            # Delete file from filesystem
            file_path = os.path.join(UPLOAD_FOLDER, self.filename)
            if os.path.exists(file_path):
                os.remove(file_path)

            return True

        except sqlite3.Error:
            conn.rollback()
            conn.close()
            return False

    def __repr__(self):
        """String representation of Resume object."""
        return f'<Resume {self.original_filename} - {self.candidate_name}>'
