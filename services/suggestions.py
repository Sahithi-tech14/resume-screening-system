import re
from models.resume import Resume


class SuggestionGenerator:
    """
    Generate improvement suggestions for resumes based on ATS analysis.
    """

    def __init__(self):
        """Initialize the suggestion generator."""
        self.suggestions = []
        # Common important sections in a resume
        self.important_sections = [
            'skills', 'experience', 'education', 'projects',
            'achievements', 'certifications', 'summary', 'objective'
        ]

        # Important action verbs for experience descriptions
        self.action_verbs = [
            'developed', 'implemented', 'designed', 'built', 'created',
            'managed', 'led', 'optimized', 'improved', 'analyzed',
            'deployed', 'automated', 'integrated', 'collaborated'
        ]

    def generate_suggestions(self, resume_text, resume_data, ats_scores, job_skills):
        """
        Generate comprehensive suggestions for resume improvement.

        Args:
            resume_text: Full text of the resume
            resume_data: Dictionary with extracted information (name, email, etc.)
            ats_scores: Dictionary with calculated ATS scores
            job_skills: List of required skills for the job

        Returns:
            List of suggestion dictionaries with type, text, and priority
        """
        self.suggestions = []

        # Generate different types of suggestions
        self._generate_skill_suggestions(resume_data, ats_scores, job_skills)
        self._generate_content_suggestions(resume_text, resume_data)
        self._generate_formatting_suggestions(resume_text)
        self._generate_keyword_suggestions(resume_text, job_skills)
        self._generate_ats_optimization_tips(ats_scores)

        # Sort by priority (lower number = higher priority)
        self.suggestions.sort(key=lambda x: x['priority'])

        return self.suggestions

    def _generate_skill_suggestions(self, resume_data, ats_scores, job_skills):
        """Generate suggestions related to skills."""
        missing_skills = ats_scores.get('missing_skills', [])

        if missing_skills:
            # Critical: Missing required skills
            priority = 1
            for skill in missing_skills[:5]:  # Limit to top 5
                self.suggestions.append({
                    'type': 'skill',
                    'text': f"Add the required skill: '{skill.title()}' is listed in the job requirements but not found in your resume.",
                    'priority': priority,
                    'category': 'Missing Skills'
                })

        # Check for skill variety
        resume_skills = resume_data.get('skills', [])
        if len(resume_skills) < 5:
            self.suggestions.append({
                'type': 'skill',
                'text': "Consider adding more technical skills. A minimum of 5-10 relevant skills is recommended for better ATS scoring.",
                'priority': 2,
                'category': 'Skill Enhancement'
            })

        # Check for skill balance
        if len(resume_skills) > 0:
            # Suggest adding both technical and soft skills
            has_soft_skills = any(skill.lower() in ['leadership', 'teamwork', 'communication',
                                                      'problem solving', 'analytical', 'management']
                                 for skill in resume_skills)
            if not has_soft_skills:
                self.suggestions.append({
                    'type': 'skill',
                    'text': "Consider adding soft skills like 'Leadership', 'Teamwork', or 'Problem Solving' to complement your technical skills.",
                    'priority': 3,
                    'category': 'Soft Skills'
                })

    def _generate_content_suggestions(self, resume_text, resume_data):
        """Generate suggestions for content improvement."""
        # Check for contact information
        if resume_data.get('email') == 'Not Found':
            self.suggestions.append({
                'type': 'content',
                'text': "Add your email address. ATS systems look for contact information at the top of the resume.",
                'priority': 1,
                'category': 'Contact Information'
            })

        if resume_data.get('phone') == 'Not Found':
            self.suggestions.append({
                'type': 'content',
                'text': "Add your phone number. Ensure it's in a standard format (e.g., +91-9876543210).",
                'priority': 1,
                'category': 'Contact Information'
            })

        # Check for education
        education = resume_data.get('education', ['Not Found'])
        if not education or education[0] == 'Not Found':
            self.suggestions.append({
                'type': 'content',
                'text': "Add an Education section with your degree, institution, and graduation year.",
                'priority': 2,
                'category': 'Education'
            })

        # Check for experience
        experience = resume_data.get('experience', ['Not Found'])
        if not experience or experience[0] == 'Not Found':
            self.suggestions.append({
                'type': 'content',
                'text': "Add your Work Experience section with company name, role, and key achievements.",
                'priority': 2,
                'category': 'Experience'
            })
        else:
            # Check for action verbs in experience
            exp_text = ' '.join(experience).lower()
            action_verb_count = sum(1 for verb in self.action_verbs if verb in exp_text)
            if action_verb_count < 3:
                self.suggestions.append({
                    'type': 'content',
                    'text': f"Use action verbs in your experience section. Examples: 'Developed', 'Implemented', 'Led', 'Optimized'.",
                    'priority': 3,
                    'category': 'Experience Quality'
                })

        # Check for projects
        projects = resume_data.get('projects', ['Not Found'])
        if not projects or projects[0] == 'Not Found':
            self.suggestions.append({
                'type': 'content',
                'text': "Consider adding a Projects section to showcase practical work and technical skills.",
                'priority': 3,
                'category': 'Projects'
            })

        # Check for certifications
        certifications = resume_data.get('certifications', ['None Found'])
        if not certifications or certifications[0] == 'None Found':
            self.suggestions.append({
                'type': 'content',
                'text': "Adding relevant certifications can boost your ATS score. Consider industry certifications like AWS, Google, or Microsoft.",
                'priority': 4,
                'category': 'Certifications'
            })

    def _generate_formatting_suggestions(self, resume_text):
        """Generate suggestions for resume formatting."""
        # Check resume length
        word_count = len(resume_text.split())
        if word_count < 200:
            self.suggestions.append({
                'type': 'format',
                'text': "Your resume appears brief. Aim for 300-500 words for entry-level positions and 500-800 for experienced roles.",
                'priority': 2,
                'category': 'Length'
            })
        elif word_count > 1000:
            self.suggestions.append({
                'type': 'format',
                'text': "Your resume is quite long. ATS systems prefer concise resumes. Consider reducing to 1-2 pages (500-800 words).",
                'priority': 3,
                'category': 'Length'
            })

        # Check for special characters that might not parse well
        special_chars = re.findall(r'[●◆◇■□]', resume_text)
        if special_chars:
            self.suggestions.append({
                'type': 'format',
                'text': "Special bullet points may not parse correctly in all ATS systems. Use standard bullets (•) or dashes (-).",
                'priority': 3,
                'category': 'Formatting'
            })

        # Check for tables/columns (heuristics)
        lines = resume_text.split('\n')
        short_lines = sum(1 for line in lines if len(line.strip()) < 30 and len(line.strip()) > 0)
        if short_lines > len(lines) * 0.5:
            self.suggestions.append({
                'type': 'format',
                'text': "Complex layouts (tables, columns) may not parse well in ATS. Use a simple, single-column format.",
                'priority': 3,
                'category': 'Layout'
            })

    def _generate_keyword_suggestions(self, resume_text, job_skills):
        """Generate suggestions for keyword optimization."""
        if not job_skills:
            return

        # Ensure job_skills is a list
        if isinstance(job_skills, str):
            try:
                import json
                job_skills = json.loads(job_skills)
            except:
                job_skills = []

        resume_lower = resume_text.lower()

        # Check for skill variations
        skill_variations = {
            'javascript': ['js', 'ecmascript', 'es6'],
            'python': ['py', 'python3'],
            'machine learning': ['ml', 'ai', 'artificial intelligence'],
            'database': ['db', 'sql', 'nosql'],
            'api': ['rest', 'restful', 'graphql', 'endpoint'],
        }

        for skill in job_skills:
            skill_lower = skill.lower()
            if skill_lower not in resume_lower:
                # Check for variations
                variations = skill_variations.get(skill_lower, [])
                found = any(v in resume_lower for v in variations)

                if not found and skill_lower not in resume_lower:
                    self.suggestions.append({
                        'type': 'keyword',
                        'text': f"Keyword '{skill}' not found. Consider including it in your Skills or Experience section.",
                        'priority': 2,
                        'category': 'Keywords'
                    })

        # Suggest adding industry keywords
        tech_keywords = ['version control', 'api', 'testing', 'debugging',
                        'optimization', 'documentation', 'code review']
        missing_keywords = [kw for kw in tech_keywords if kw not in resume_lower]

        if missing_keywords:
            self.suggestions.append({
                'type': 'keyword',
                'text': f"Consider adding industry keywords: {', '.join(missing_keywords[:3])}. These are commonly searched by recruiters.",
                'priority': 4,
                'category': 'Keywords'
            })

    def _generate_ats_optimization_tips(self, ats_scores):
        """Generate ATS-specific optimization tips."""
        overall_score = ats_scores.get('overall_ats_score', 0)
        skill_score = ats_scores.get('skill_match_score', 0)
        keyword_score = ats_scores.get('keyword_match_score', 0)
        relevance_score = ats_scores.get('relevance_score', 0)

        # Overall score suggestions
        if overall_score < 40:
            self.suggestions.append({
                'type': 'ats',
                'text': "Your ATS score is low. Focus on adding missing skills and keywords that match the job description.",
                'priority': 1,
                'category': 'ATS Score'
            })
        elif overall_score < 60:
            self.suggestions.append({
                'type': 'ats',
                'text': "Your ATS score is moderate. Tailor your resume more specifically to the job requirements.",
                'priority': 2,
                'category': 'ATS Score'
            })
        elif overall_score >= 80:
            self.suggestions.append({
                'type': 'ats',
                'text': f"Great! Your ATS score is {overall_score:.1f}%. Your resume is well-optimized for this job.",
                'priority': 5,
                'category': 'ATS Score'
            })

        # Specific score improvements
        if keyword_score < 50:
            self.suggestions.append({
                'type': 'ats',
                'text': "Keyword match is low. Mirror the terminology used in the job description in your resume.",
                'priority': 2,
                'category': 'Keyword Match'
            })

        if relevance_score < 50:
            self.suggestions.append({
                'type': 'ats',
                'text': "Content relevance could be improved. Ensure your experience descriptions align with job requirements.",
                'priority': 3,
                'category': 'Relevance'
            })

        # General ATS tips
        self.suggestions.append({
            'type': 'ats',
            'text': "Use standard section headings: 'Experience', 'Education', 'Skills'. Creative headings may confuse ATS.",
            'priority': 4,
            'category': 'ATS Tips'
        })

        self.suggestions.append({
            'type': 'ats',
            'text': "Save your resume as PDF or DOCX. These formats are most ATS-friendly.",
            'priority': 5,
            'category': 'ATS Tips'
        })

    def get_suggestions_by_category(self, suggestions=None):
        """Group suggestions by category."""
        if suggestions is None:
            suggestions = self.suggestions

        categories = {}
        for suggestion in suggestions:
            category = suggestion.get('category', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(suggestion)

        return categories


def generate_resume_suggestions(resume_text, resume_data, ats_scores, job_skills):
    """
    Convenience function to generate suggestions.

    Args:
        resume_text: Full text from resume
        resume_data: Extracted information dictionary
        ats_scores: Calculated ATS scores
        job_skills: Required skills list

    Returns:
        List of suggestions sorted by priority
    """
    generator = SuggestionGenerator()
    return generator.generate_suggestions(resume_text, resume_data, ats_scores, job_skills)


# Example usage
if __name__ == '__main__':
    # Test the suggestion generator
    sample_resume_data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+91-9876543210',
        'skills': ['Python', 'JavaScript', 'React'],
        'education': ['B.Tech Computer Science'],
        'experience': ['Software Developer at ABC Corp'],
        'certifications': ['None Found'],
        'projects': ['Not Found']
    }

    sample_ats_scores = {
        'overall_ats_score': 55,
        'skill_match_score': 50,
        'keyword_match_score': 40,
        'relevance_score': 60,
        'missing_skills': ['Node.js', 'MongoDB', 'Git']
    }

    job_skills = ['Python', 'JavaScript', 'React', 'Node.js', 'MongoDB', 'Git']

    generator = SuggestionGenerator()
    suggestions = generator.generate_suggestions(
        "Sample resume text with Python and JavaScript skills...",
        sample_resume_data,
        sample_ats_scores,
        job_skills
    )

    print("Generated Suggestions:\n")
    for i, suggestion in enumerate(suggestions[:10], 1):
        print(f"{i}. [{suggestion['category']}] (Priority {suggestion['priority']})")
        print(f"   {suggestion['text']}\n")
