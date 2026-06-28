"""
Resume Routes - Handles resume upload, processing, and analysis.

WHY THIS FILE IS REQUIRED:
- Main functionality for resume upload and processing
- Coordinates parser, NLP, ATS calculator, and suggestions
- Handles file validation and storage

WHAT THIS FILE DOES:
- Upload: Accepts PDF/DOCX files
- Process: Extracts text, parses resume, calculates scores
- Analyze: Generates suggestions and stores results
- History: Shows uploaded resumes

HOW IT CONNECTS TO OTHER FILES:
- Uses parser service for text extraction
- Uses NLP service for information extraction
- Uses ATS calculator for scoring
- Uses suggestion generator for recommendations

INTERVIEW PREPARATION:

Q: Why use secure_filename?
A: User-provided filenames can contain path traversal characters
   (../) that could allow writing files outside the upload directory.
   secure_filename removes these dangerous characters.

Q: Why check file extension on both client and server?
A: Client-side validation improves user experience.
   Server-side validation is essential for security.

Q: What is the processing pipeline?
A: Upload -> Parse -> NLP Extract -> ATS Score -> Generate Suggestions
   Each step transforms the data for the next step.
"""

import os
import json
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from models.resume import Resume
from services.parser import extract_text
from services.nlp import NLPProcessor
from services.ats_calculator import calculate_ats_score
from services.suggestions import generate_resume_suggestions
from database.init_db import get_db_connection
from config import DATABASE_PATH, UPLOAD_FOLDER, ALLOWED_EXTENSIONS

# Create resume blueprint
resume_bp = Blueprint('resume', __name__)


def allowed_file(filename):
    """
    Check if the file has an allowed extension.

    Args:
        filename: Name of the uploaded file

    Returns:
        True if extension is allowed, False otherwise
    """
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


@resume_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """
    Handle resume upload.

    GET: Display upload form
    POST: Process uploaded file

    Returns:
        Redirect to analysis on success, upload form otherwise
    """
    if request.method == 'POST':
        # Get job information from form
        job_title = request.form.get('job_title', '').strip()
        job_description = request.form.get('job_description', '').strip()

        # Validate job information
        if not job_title:
            flash('Please enter a job title.', 'error')
            return redirect(request.url)

        if not job_description:
            flash('Please enter a job description.', 'error')
            return redirect(request.url)

        # Store in session for later analysis
        session['job_title'] = job_title
        session['job_description'] = job_description

        print("JOB TITLE:", job_title)
        print("JOB DESCRIPTION:", job_description[:200])

        # Check if file was uploaded
        if 'resume' not in request.files:
            flash('No file selected.', 'error')
            return redirect(request.url)

        file = request.files['resume']

        # Check if file was selected
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)

        # Check file extension
        if not allowed_file(file.filename):
            flash('Invalid file format. Please upload PDF or DOCX files only.', 'error')
            return redirect(request.url)

        # Create secure filename
        original_filename = file.filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{current_user.id}_{timestamp}_{secure_filename(original_filename)}"

        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Save the file
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Create resume record
        resume = Resume.create(
            user_id=current_user.id,
            filename=filename,
            original_filename=original_filename
        )

        if not resume:
            flash('Error saving resume. Please try again.', 'error')
            return redirect(request.url)

        # Extract text from file
        extracted_text = extract_text(filename)

        if not extracted_text:
            flash('Could not extract text from the file. Please check the file format.', 'error')
            return redirect(request.url)

        # Update resume with extracted text
        resume.update_extracted_text(extracted_text)

        # Redirect to processing page
        flash('Resume uploaded successfully! Processing...', 'success')
        return redirect(url_for('resume.analyze', resume_id=resume.id))

    return render_template('upload.html')


@resume_bp.route('/analyze/<int:resume_id>')
@login_required
def analyze(resume_id):
    """
    Analyze a resume and calculate ATS score.

    Args:
        resume_id: ID of the resume to analyze

    Returns:
        Redirect to results page
    """
    # Get resume
    resume = Resume.get_by_id(resume_id)

    if not resume:
        flash('Resume not found.', 'error')
        return redirect(url_for('dashboard.home'))

    # Check ownership
    if resume.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard.home'))

    # Get job information from session
    job_title = session.get('job_title')
    job_description = session.get('job_description')

    if not job_description:
        flash('Please provide a job description.', 'error')
        return redirect(url_for('resume.upload'))

    # Process resume text with NLP
    processor = NLPProcessor()
    resume_data = processor.process_resume(resume.extracted_text)

    # Extract skills from job description
    job_processor = NLPProcessor()
    job_data = job_processor.process_resume(job_description)
    job_skills = job_data.get('skills', [])

    # Update resume with parsed data
    resume.update_parsed_data(
        candidate_name=resume_data.get('name'),
        email=resume_data.get('email'),
        phone=resume_data.get('phone'),
        skills=resume_data.get('skills', []),
        education=resume_data.get('education', ['Not Found'])[0] if resume_data.get('education') else None,
        experience=resume_data.get('experience', ['Not Found'])[0] if resume_data.get('experience') else None,
        certifications=resume_data.get('certifications', ['None Found'])[0] if resume_data.get('certifications') else None,
        projects=resume_data.get('projects', ['Not Found'])[0] if resume_data.get('projects') else None
    )

    # Calculate ATS scores
    ats_scores = calculate_ats_score(
        resume_text=resume.extracted_text,
        resume_skills=resume_data.get('skills', []),
        job_description=job_description,
        job_skills=job_skills,
        resume_id=resume.id,
        job_id=None  # No stored job, using session data
    )

    # Generate suggestions
    suggestions = generate_resume_suggestions(
        resume_text=resume.extracted_text,
        resume_data=resume_data,
        ats_scores=ats_scores,
        job_skills=job_skills
    )

    # Store suggestions in database
    store_suggestions(resume.id, suggestions)

    flash('Resume analysis complete!', 'success')
    return redirect(url_for('resume.result', resume_id=resume.id))


@resume_bp.route('/result/<int:resume_id>')
@login_required
def result(resume_id):
    """
    Display analysis results.

    Args:
        resume_id: ID of the resume

    Returns:
        Results page with scores and suggestions
    """
    # Get resume
    resume = Resume.get_by_id(resume_id)

    if not resume:
        flash('Resume not found.', 'error')
        return redirect(url_for('dashboard.home'))

    # Check ownership
    if resume.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard.home'))

    # Get ATS score
    from models.ats import ATSScore
    ats_score = ATSScore.get_by_resume(resume_id)

    # Get suggestions
    suggestions = get_suggestions(resume_id)

    # Get job info from session
    job = {
        'title': session.get('job_title', 'Custom Job'),
        'description': session.get('job_description', '')
    }

    # Extract skills from job description
    job_skills = []
    if job['description']:
        processor = NLPProcessor()
        job_data = processor.process_resume(job['description'])
        job_skills = job_data.get('skills', [])

    return render_template('result.html',
                           resume=resume,
                           ats_score=ats_score,
                           suggestions=suggestions,
                           job=job,
                           job_skills=job_skills)


@resume_bp.route('/history')
@login_required
def history():
    """
    Display upload history.

    Returns:
        History page with all user's resumes
    """
    resumes = Resume.get_by_user(current_user.id)

    # Get scores for each resume
    from models.ats import ATSScore
    resumes_with_scores = []
    for resume in resumes:
        score = ATSScore.get_by_resume(resume.id)
        resumes_with_scores.append({
            'resume': resume,
            'score': score
        })

    return render_template('history.html', resumes=resumes_with_scores)


@resume_bp.route('/compare')
@login_required
def compare():
    """
    Compare multiple resumes for candidate ranking.

    Returns:
        Ranking page with sorted candidates
    """
    from models.ats import ATSScore

    # Get all scores with ranking
    ranked_scores = ATSScore.get_all_scores()

    return render_template('compare.html', ranked_scores=ranked_scores)


@resume_bp.route('/delete/<int:resume_id>')
@login_required
def delete(resume_id):
    """
    Delete a resume.

    Args:
        resume_id: ID of the resume to delete

    Returns:
        Redirect to history
    """
    resume = Resume.get_by_id(resume_id)

    if not resume:
        flash('Resume not found.', 'error')
        return redirect(url_for('resume.history'))

    if resume.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('resume.history'))

    # Delete ATS scores first
    conn = get_db_connection(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM ats_scores WHERE resume_id = ?', (resume_id,))
    cursor.execute('DELETE FROM suggestions WHERE resume_id = ?', (resume_id,))
    conn.commit()
    conn.close()

    # Delete resume
    resume.delete()

    flash('Resume deleted successfully.', 'success')
    return redirect(url_for('resume.history'))


def store_suggestions(resume_id, suggestions):
    """
    Store suggestions in database.

    Args:
        resume_id: ID of the resume
        suggestions: List of suggestion dictionaries
    """
    conn = get_db_connection(DATABASE_PATH)
    cursor = conn.cursor()

    for suggestion in suggestions[:10]:  # Store top 10 suggestions
        cursor.execute(
            '''INSERT INTO suggestions (resume_id, suggestion_type, suggestion_text, priority)
               VALUES (?, ?, ?, ?)''',
            (resume_id, suggestion.get('type', 'general'),
             suggestion.get('text', ''), suggestion.get('priority', 1))
        )

    conn.commit()
    conn.close()


def get_suggestions(resume_id):
    """
    Retrieve suggestions for a resume.

    Args:
        resume_id: ID of the resume

    Returns:
        List of suggestion dictionaries
    """
    conn = get_db_connection(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        'SELECT * FROM suggestions WHERE resume_id = ? ORDER BY priority',
        (resume_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    suggestions = []
    for row in rows:
        suggestions.append({
            'id': row['id'],
            'type': row['suggestion_type'],
            'text': row['suggestion_text'],
            'priority': row['priority'],
            'category': getattr(row, 'category', 'General')
        })

    return suggestions
