
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import SKILL_WEIGHT, KEYWORD_WEIGHT, RELEVANCE_WEIGHT
from models.ats import ATSScore
import json


class ATSCalculator:
    """
    Calculate ATS compatibility scores using ML techniques.
    """

    def __init__(self):
        """Initialize the TF-IDF vectorizer."""
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),  # Use unigrams and bigrams
            max_features=5000,  # Limit vocabulary size
            min_df=1,  # Minimum document frequency
        )

    def calculate_scores(self, resume_text, resume_skills, job_description, job_skills):
        """
        Calculate all ATS scores for a resume-job pair.

        Args:
            resume_text: Full text extracted from resume
            resume_skills: List of skills from resume
            job_description: Full job description text
            job_skills: List of required skills for the job

        Returns:
            Dictionary containing:
            - skill_match_score: Percentage of job skills present in resume
            - keyword_match_score: Similarity based on keywords
            - relevance_score: Overall document similarity
            - overall_ats_score: Weighted combination
            - matched_skills: Skills that matched
            - missing_skills: Skills not found in resume
        """
        # Calculate individual scores
        skill_result = self.calculate_skill_match(resume_skills, job_skills)
        keyword_score = self.calculate_keyword_match(resume_text, job_description)
        relevance_score = self.calculate_relevance_score(resume_text, job_description)

        # Calculate overall score with weights
        overall_score = (
            skill_result['score'] * SKILL_WEIGHT +
            keyword_score * KEYWORD_WEIGHT +
            relevance_score * RELEVANCE_WEIGHT
        )

        return {
            'skill_match_score': round(skill_result['score'], 2),
            'keyword_match_score': round(keyword_score, 2),
            'relevance_score': round(relevance_score, 2),
            'overall_ats_score': round(overall_score, 2),
            'matched_skills': skill_result['matched_skills'],
            'missing_skills': skill_result['missing_skills'],
            'skill_count': len(resume_skills),
            'required_skill_count': len(job_skills)
        }

    def calculate_skill_match(self, resume_skills, job_skills):
        """
        Calculate skill matching score.

        Compares resume skills with required job skills.

        Args:
            resume_skills: List of skills from resume
            job_skills: List of required skills

        Returns:
            Dictionary with score, matched skills, and missing skills
        """
        # Ensure job_skills is a list
        if isinstance(job_skills, str):
            try:
                job_skills = json.loads(job_skills)
            except json.JSONDecodeError:
                job_skills = []

        # Normalize skills for comparison
        resume_skills_lower = set(s.lower() for s in resume_skills if s)
        job_skills_lower = set(s.lower() for s in job_skills if s)

        # Find matches
        matched = resume_skills_lower.intersection(job_skills_lower)
        missing = job_skills_lower - resume_skills_lower

        # Calculate score (percentage of required skills present)
        if len(job_skills_lower) > 0:
            score = (len(matched) / len(job_skills_lower)) * 100
        else:
            score = 0

        return {
            'score': score,
            'matched_skills': sorted(list(matched)),
            'missing_skills': sorted(list(missing))
        }

    def calculate_keyword_match(self, resume_text, job_description):
        """
        Calculate keyword matching using TF-IDF.

        Compares important terms in both documents.

        Args:
            resume_text: Full resume text
            job_description: Full job description

        Returns:
            Similarity score between 0-100
        """
        if not resume_text or not job_description:
            return 0

        try:
            # Create TF-IDF vectors for both documents
            tfidf_matrix = self.vectorizer.fit_transform([resume_text, job_description])

            # Extract keywords from job description
            feature_names = self.vectorizer.get_feature_names_out()

            # Get TF-IDF scores for job description
            job_tfidf = tfidf_matrix[1].toarray()[0]

            # Get top keywords from job description
            top_indices = job_tfidf.argsort()[-20:][::-1]  # Top 20 keywords

            job_keywords = set(feature_names[i] for i in top_indices if job_tfidf[i] > 0)

            # Check which keywords appear in resume
            resume_text_lower = resume_text.lower()

            matched_keywords = sum(1 for kw in job_keywords if kw in resume_text_lower)

            # Calculate match percentage
            if len(job_keywords) > 0:
                score = (matched_keywords / len(job_keywords)) * 100
            else:
                score = 0

            return min(score, 100)

        except Exception as e:
            print(f"Error in keyword matching: {str(e)}")
            return 0

    def calculate_relevance_score(self, resume_text, job_description):
        """
        Calculate overall document relevance using cosine similarity.

        This measures how similar the entire documents are.

        Args:
            resume_text: Full resume text
            job_description: Full job description

        Returns:
            Similarity score between 0-100
        """
        if not resume_text or not job_description:
            return 0

        try:
            # Create a new vectorizer for full document comparison
            vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words='english',
                ngram_range=(1, 2),
                max_features=10000
            )

            # Create TF-IDF matrix
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])

            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

            # Convert to percentage
            score = similarity[0][0] * 100

            return min(max(score, 0), 100)

        except Exception as e:
            print(f"Error in relevance calculation: {str(e)}")
            return 0

    def compare_multiple_resumes(self, resumes_data, job_description, job_skills):
        """
        Compare multiple resumes against a job description.

        Args:
            resumes_data: List of dicts with 'id', 'text', 'skills'
            job_description: Full job description
            job_skills: Required skills list

        Returns:
            Ranked list of resumes with scores
        """
        results = []

        for resume_data in resumes_data:
            scores = self.calculate_scores(
                resume_data['text'],
                resume_data['skills'],
                job_description,
                job_skills
            )

            results.append({
                'resume_id': resume_data['id'],
                'candidate_name': resume_data.get('name', 'Unknown'),
                'scores': scores
            })

        # Sort by overall ATS score (descending)
        results.sort(key=lambda x: x['scores']['overall_ats_score'], reverse=True)

        # Add ranking
        for i, result in enumerate(results, 1):
            result['rank'] = i

        return results


def calculate_ats_score(resume_text, resume_skills, job_description, job_skills, resume_id=None, job_id=None):
    """
    Convenience function to calculate and store ATS score.

    Args:
        resume_text: Full resume text
        resume_skills: List of skills from resume
        job_description: Full job description
        job_skills: Required skills for the job
        resume_id: Database ID of the resume (optional)
        job_id: Database ID of the job (optional)

    Returns:
        Dictionary with all scores
    """
    calculator = ATSCalculator()
    scores = calculator.calculate_scores(resume_text, resume_skills, job_description, job_skills)

    # Store in database if IDs provided
    if resume_id:
        ATSScore.create(
            resume_id=resume_id,
            job_id=job_id,
            skill_match_score=scores['skill_match_score'],
            keyword_match_score=scores['keyword_match_score'],
            relevance_score=scores['relevance_score'],
            overall_ats_score=scores['overall_ats_score']
        )

    return scores


# Example usage
if __name__ == '__main__':
    # Test the calculator
    sample_resume = """
    John Doe
    Software Developer

    Skills: Python, JavaScript, React, Node.js, SQL, MongoDB, Git, Docker

    Experience:
    Developed web applications using Python and Flask.
    Built frontend using React and integrated with REST APIs.
    """

    sample_job = """
    Software Developer

    Required Skills: Python, JavaScript, React, Node.js, SQL, MongoDB

    We are looking for a developer with experience in:
    - Python and web frameworks (Flask/Django)
    - React for frontend development
    - Database experience with SQL and NoSQL
    - Git version control
    """

    calculator = ATSCalculator()
    resume_skills = ['Python', 'JavaScript', 'React', 'Node.js', 'SQL', 'MongoDB', 'Git', 'Docker']
    job_skills = ['Python', 'JavaScript', 'React', 'Node.js', 'SQL', 'MongoDB']

    scores = calculator.calculate_scores(sample_resume, resume_skills, sample_job, job_skills)

    print("ATS Scores:")
    print(f"Skill Match: {scores['skill_match_score']}%")
    print(f"Keyword Match: {scores['keyword_match_score']}%")
    print(f"Relevance: {scores['relevance_score']}%")
    print(f"Overall ATS Score: {scores['overall_ats_score']}%")
    print(f"\nMatched Skills: {', '.join(scores['matched_skills'])}")
    print(f"Missing Skills: {', '.join(scores['missing_skills'])}")
