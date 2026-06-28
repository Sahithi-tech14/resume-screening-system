import sqlite3
from datetime import datetime
from database.init_db import get_db_connection
from config import DATABASE_PATH


class ATSScore:
    """
    ATS Score class for storing and retrieving score data.
    """

    def __init__(self, id, resume_id, job_id, skill_match_score,
                 keyword_match_score, relevance_score, overall_ats_score, calculation_date):
        """
        Initialize an ATSScore instance.
        """
        self.id = id
        self.resume_id = resume_id
        self.job_id = job_id
        self.skill_match_score = skill_match_score
        self.keyword_match_score = keyword_match_score
        self.relevance_score = relevance_score
        self.overall_ats_score = overall_ats_score
        self.calculation_date = calculation_date

    @staticmethod
    def get_by_resume(resume_id):
        """
        Retrieve the latest ATS score for a resume.

        Args:
            resume_id: The resume's ID

        Returns:
            ATSScore object if found, None otherwise
        """
        conn = get_db_connection(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            '''SELECT * FROM ats_scores
               WHERE resume_id = ?
               ORDER BY calculation_date DESC LIMIT 1''',
            (resume_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return ATSScore(
                id=row['id'],
                resume_id=row['resume_id'],
                job_id=row['job_id'],
                skill_match_score=row['skill_match_score'],
                keyword_match_score=row['keyword_match_score'],
                relevance_score=row['relevance_score'],
                overall_ats_score=row['overall_ats_score'],
                calculation_date=row['calculation_date']
            )
        return None

    @staticmethod
    def get_all_scores():
        """
        Retrieve all ATS scores for ranking.

        Returns:
            List of ATSScore objects with resume info
        """
        conn = get_db_connection(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            '''SELECT a.*, r.candidate_name, r.original_filename, r.email
               FROM ats_scores a
               JOIN resumes r ON a.resume_id = r.id
               ORDER BY a.overall_ats_score DESC'''
        )
        rows = cursor.fetchall()
        conn.close()

        scores = []
        for row in rows:
            scores.append({
                'id': row['id'],
                'resume_id': row['resume_id'],
                'candidate_name': row['candidate_name'],
                'filename': row['original_filename'],
                'email': row['email'],
                'skill_match_score': row['skill_match_score'],
                'keyword_match_score': row['keyword_match_score'],
                'relevance_score': row['relevance_score'],
                'overall_ats_score': row['overall_ats_score'],
                'calculation_date': row['calculation_date']
            })
        return scores

    @staticmethod
    def create(resume_id, job_id, skill_match_score, keyword_match_score,
               relevance_score, overall_ats_score):
        """
        Create a new ATS score record.

        Args:
            resume_id: The resume being scored
            job_id: The job description used for matching
            skill_match_score: Score for skill matching
            keyword_match_score: Score for keyword matching
            relevance_score: Score for overall relevance
            overall_ats_score: Combined ATS score

        Returns:
            ATSScore object if successful, None otherwise
        """
        conn = get_db_connection(DATABASE_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute(
                '''INSERT INTO ats_scores
                   (resume_id, job_id, skill_match_score, keyword_match_score,
                    relevance_score, overall_ats_score)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (resume_id, job_id, skill_match_score, keyword_match_score,
                 relevance_score, overall_ats_score)
            )
            conn.commit()
            score_id = cursor.lastrowid
            conn.close()

            return ATSScore.get_by_resume(resume_id)

        except sqlite3.Error:
            conn.rollback()
            conn.close()
            return None

    def __repr__(self):
        """String representation of ATSScore object."""
        return f'<ATSScore Resume:{self.resume_id} Score:{self.overall_ats_score}%>'
