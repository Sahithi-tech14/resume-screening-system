"""
Dashboard Routes - Main dashboard for the application.

WHY THIS FILE IS REQUIRED:
- Central hub for user interaction
- Displays overview of resume analysis
- Shows performance metrics and rankings

WHAT THIS FILE DOES:
- Shows home page with summary
- Displays performance charts
- Shows candidate rankings
- Provides navigation to other features

INTERVIEW PREPARATION:

Q: Why separate dashboard from resume routes?
A: Single Responsibility Principle. Dashboard shows overview,
   resume routes handle specific resume operations.
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.resume import Resume
from models.ats import ATSScore
from database.init_db import get_db_connection
from config import DATABASE_PATH

# Create dashboard blueprint
dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def home():
    """
    Display the main dashboard.

    Returns:
        Dashboard page with overview statistics
    """
    # Get user's resumes
    resumes = Resume.get_by_user(current_user.id)

    # Get all scores for charts
    all_scores = ATSScore.get_all_scores()

    # Calculate statistics
    total_resumes = len(resumes)
    avg_score = 0
    max_score = 0

    user_scores = [s for s in all_scores if s.get('resume_id') in [r.id for r in resumes]]
    if user_scores:
        avg_score = sum(s['overall_ats_score'] for s in user_scores) / len(user_scores)
        max_score = max(s['overall_ats_score'] for s in user_scores)

    # Recent resumes (last 5)
    recent_resumes = resumes[:5]

    # Get job information
    conn = get_db_connection(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs LIMIT 1')
    job = cursor.fetchone()
    conn.close()

    return render_template('dashboard.html',
                         total_resumes=total_resumes,
                         avg_score=round(avg_score, 1),
                         max_score=round(max_score, 1),
                         recent_resumes=recent_resumes,
                         all_scores=all_scores[:10],
                         job=job,
                         user=current_user)


@dashboard_bp.route('/profile')
@login_required
def profile():
    """
    Display user profile page.

    Returns:
        Profile page with user information
    """
    return render_template('profile.html', user=current_user)


@dashboard_bp.route('/rankings')
@login_required
def rankings():
    """
    Display candidate rankings.

    Returns:
        Rankings page with all candidates sorted by score
    """
    # Get all scores with rankings
    ranked_scores = ATSScore.get_all_scores()

    return render_template('rankings.html', ranked_scores=ranked_scores)
