
import re
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data (only downloads if not present)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)


# Common technical skills database
TECHNICAL_SKILLS = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c', 'c#', 'ruby',
    'go', 'rust', 'swift', 'kotlin', 'php', 'perl', 'scala', 'r', 'matlab',

    # Web Technologies
    'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django',
    'flask', 'spring', 'bootstrap', 'jquery', 'sass', 'less', 'webpack',

    # Databases
    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite',
    'cassandra', 'dynamodb', 'firebase', 'elasticsearch',

    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github',
    'gitlab', 'ci/cd', 'terraform', 'ansible', 'linux', 'unix',

    # Data Science & ML
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras',
    'pandas', 'numpy', 'scikit-learn', 'matplotlib', 'nlp', 'computer vision',
    'data science', 'ai', 'artificial intelligence',

    # Mobile Development
    'android', 'ios', 'react native', 'flutter', 'xamarin',

    # Other
    'api', 'rest', 'graphql', 'microservices', 'agile', 'scrum', 'api',
    'selenium', 'testing', 'junit', 'pytest', 'oop', 'data structures',
    'algorithms', 'problem solving', 'leadership', 'teamwork'
}


class NLPProcessor:
    """
    Process resume text using NLP techniques.
    Extracts structured information for ATS scoring.
    """

    def __init__(self):
        """Initialize NLP components."""
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

        # Add resume-specific stopwords
        self.stop_words.update(['resume', 'cv', 'curriculum', 'vitae'])

    def process_resume(self, text):
        """
        Full NLP processing of resume text.

        Args:
            text: Raw text extracted from resume

        Returns:
            Dictionary with all extracted information
        """
        if not text:
            return {}

        result = {
            'name': self.extract_name(text),
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'skills': self.extract_skills(text),
            'education': self.extract_education(text),
            'experience': self.extract_experience(text),
            'certifications': self.extract_certifications(text),
            'projects': self.extract_projects(text),
            'keywords': self.extract_keywords(text),
            'clean_tokens': self.tokenize_and_clean(text),
            'lemmatized_tokens': self.lemmatize_text(text)
        }

        return result

    def extract_name(self, text):
        """
        Extract candidate name from resume.
        Usually at the beginning of the resume.

        Uses multiple heuristics:
        1. First non-empty line (common in resumes)
        2. Line before email/phone (common pattern)
        3. Line with only capitalized words
        """
        lines = text.strip().split('\n')

        # Check first few lines for name
        for line in lines[:5]:
            line = line.strip()
            if not line or len(line) < 3 or len(line) > 50:
                continue

            # Skip lines that look like contact info
            if '@' in line or any(char.isdigit() for char in line):
                continue

            # Skip lines with common resume words
            resume_words = ['resume', 'curriculum', 'vitae', 'address',
                            'objective', 'summary', 'profile']
            if any(word in line.lower() for word in resume_words):
                continue

            # If line has 2-4 words and mostly letters, it's likely a name
            words = line.split()
            if 2 <= len(words) <= 4:
                if all(word[0].isupper() or word.isupper() for word in words if word):
                    # Clean up the name
                    name = ' '.join(words)
                    # Remove any remaining special characters
                    name = re.sub(r'[^a-zA-Z\s]', '', name).strip()
                    if name:
                        return name

        return "Not Found"

    def extract_email(self, text):
        """
        Extract email address using regex.

        Pattern matches: username@domain.extension
        """
        # Email regex pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        matches = re.findall(email_pattern, text)
        return matches[0] if matches else "Not Found"

    def extract_phone(self, text):
        """
        Extract phone number using regex.
        Handles multiple formats:
        - +91-9876543210
        - 9876543210
        - 9876-543-210
        """
        # Various phone number patterns
        patterns = [
            r'\+?\d{1,3}[-.\s]?\d{10}',  # International format
            r'\+?\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # With separators
            r'\b\d{10}\b',  # Simple 10 digit
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Clean the phone number
                phone = matches[0]
                return phone

        return "Not Found"

    def extract_skills(self, text):
        """
        Extract technical skills from resume text.

        Compares text against predefined skill database.
        Uses word boundaries to avoid partial matches.
        """
        found_skills = set()
        text_lower = text.lower()

        # Tokenize to get individual words
        tokens = self.tokenize_and_clean(text_lower)

        # Check for multi-word skills first
        for skill in TECHNICAL_SKILLS:
            if ' ' in skill:
                if skill in text_lower:
                    found_skills.add(skill.title())
            else:
                if skill in tokens:
                    found_skills.add(skill.title())

        # Check for skills not in database using patterns
        # Look for common skill section headers
        skill_section_patterns = [
            r'skills?[:\s]+([^,\n]+)',
            r'technical\s+skills?[:\s]+([^,\n]+)',
            r'technologies[:\s]+([^,\n]+)',
            r'proficient\s+in[:\s]+([^,\n]+)',
        ]

        for pattern in skill_section_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                # Split by common separators
                for skill in re.split(r'[,;|]', match):
                    skill = skill.strip()
                    if len(skill) > 2:
                        found_skills.add(skill.title())

        return sorted(list(found_skills))

    def extract_education(self, text):
        """
        Extract education information.

        Looks for degrees, colleges, and years.
        """
        education_info = []

        # Education-related keywords
        edu_keywords = ['education', 'degree', 'bachelor', 'master', 'phd',
                        'b.tech', 'm.tech', 'b.e', 'm.e', 'bca', 'mca',
                        'b.sc', 'm.sc', 'mba', 'college', 'university',
                        'school', 'institute', 'iit', 'nit', 'iiit']

        lines = text.split('\n')

        for i, line in enumerate(lines):
            line_lower = line.lower()

            # Check if line contains education keywords
            if any(keyword in line_lower for keyword in edu_keywords):
                # Get the line and possibly next few lines
                edu_text = line.strip()

                # Check next lines for more info
                for j in range(i + 1, min(i + 3, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not any(kw in next_line.lower() for kw in ['experience', 'skills', 'projects']):
                        edu_text += " " + next_line
                    else:
                        break

                if len(edu_text) > 10:
                    education_info.append(edu_text.strip())

        # Also look for year patterns like "2020-2024" or "Graduated 2023"
        grad_pattern = r'\b(20\d{2})\b'
        years = re.findall(grad_pattern, text)

        return education_info if education_info else ["Not Found"]

    def extract_experience(self, text):
        """
        Extract work experience information.

        Looks for company names, job titles, and duration.
        """
        experience_info = []

        # Experience-related keywords
        exp_keywords = ['experience', 'work experience', 'employment',
                        'worked', 'position', 'role', 'company',
                        'organization', 'intern']

        # Job title patterns
        job_titles = ['developer', 'engineer', 'manager', 'analyst',
                      'consultant', 'lead', 'senior', 'junior', 'intern',
                      'architect', 'designer', 'director', 'administrator']

        lines = text.split('\n')

        in_experience_section = False

        for i, line in enumerate(lines):
            line_lower = line.lower()

            # Check if entering experience section
            if any(keyword in line_lower for keyword in exp_keywords):
                in_experience_section = True
                continue

            # If in experience section, look for job entries
            if in_experience_section:
                # Check for job title
                if any(title in line_lower for title in job_titles):
                    exp_text = line.strip()

                    # Check next lines for company and duration
                    for j in range(i + 1, min(i + 3, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and len(next_line) > 5:
                            exp_text += " " + next_line
                        else:
                            break

                    if len(exp_text) > 10:
                        experience_info.append(exp_text.strip())

                # End of experience section
                if any(kw in line_lower for kw in ['education', 'skills', 'projects', 'certification']):
                    in_experience_section = False

        return experience_info if experience_info else ["Not Found"]

    def extract_certifications(self, text):
        """
        Extract certification information.
        """
        certifications = []

        # Certification keywords
        cert_keywords = ['certified', 'certification', 'certificate',
                        'aws certified', 'google certified', 'microsoft',
                        'oracle certified', 'pmp', 'scrum', 'cisco']

        lines = text.split('\n')

        for i, line in enumerate(lines):
            line_lower = line.lower()

            if any(keyword in line_lower for keyword in cert_keywords):
                cert_text = line.strip()
                if len(cert_text) > 5 and len(cert_text) < 200:
                    certifications.append(cert_text)

        return certifications if certifications else ["None Found"]

    def extract_projects(self, text):
        """
        Extract project information.
        """
        projects = []

        # Project section keywords
        proj_keywords = ['project', 'project title', 'academic project',
                         'personal project', 'mini project', 'major project']

        lines = text.split('\n')
        in_project_section = False

        for i, line in enumerate(lines):
            line_lower = line.lower()

            if any(keyword in line_lower for keyword in proj_keywords):
                in_project_section = True
                # Get project title/description
                proj_text = line.strip()
                if len(proj_text) > 10:
                    projects.append(proj_text)
                continue

            # End of project section
            if in_project_section:
                if any(kw in line_lower for kw in ['education', 'skills', 'experience', 'achievement']):
                    in_project_section = False

        return projects if projects else ["Not Found"]

    def tokenize_and_clean(self, text):
        """
        Tokenize text and remove stopwords.

        Args:
            text: Text to tokenize

        Returns:
            List of cleaned tokens
        """
        # Tokenize
        tokens = word_tokenize(text.lower())

        # Remove non-alphabetic tokens and stopwords
        cleaned_tokens = []
        for token in tokens:
            # Keep only alphabetic tokens
            if token.isalpha() and len(token) > 1:
                # Remove stopwords
                if token not in self.stop_words:
                    cleaned_tokens.append(token)

        return cleaned_tokens

    def lemmatize_text(self, text):
        """
        Lemmatize text to convert words to base form.

        Args:
            text: Text to lemmatize

        Returns:
            List of lemmatized tokens
        """
        tokens = self.tokenize_and_clean(text)
        lemmatized = [self.lemmatizer.lemmatize(token) for token in tokens]
        return lemmatized

    def extract_keywords(self, text):
        """
        Extract important keywords from text.

        Uses frequency analysis to find important terms.

        Returns:
            List of important keywords
        """
        tokens = self.tokenize_and_clean(text)

        # Count token frequencies
        from collections import Counter
        freq = Counter(tokens)

        # Get top keywords (appearing more than once)
        keywords = [word for word, count in freq.most_common(20) if count >= 1]

        return keywords

    def extract_sentence_tokens(self, text):
        """
        Split text into sentences.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        sentences = sent_tokenize(text)
        return sentences


# Convenience function
def process_resume_text(text):
    """
    Process resume text and return structured data.

    Args:
        text: Raw resume text

    Returns:
        Dictionary with extracted information
    """
    processor = NLPProcessor()
    return processor.process_resume(text)


if __name__ == '__main__':
    # Test the processor
    sample_text = """
    John Doe
    Software Developer
    Email: john.doe@email.com
    Phone: +91-9876543210

    SKILLS:
    Python, JavaScript, React, Node.js, SQL, MongoDB, Git, Docker

    EXPERIENCE:
    Senior Developer at ABC Corp
    Developed web applications using Python and React

    EDUCATION:
    B.Tech in Computer Science
    IIT Delhi (2014-2018)

    PROJECTS:
    E-commerce Platform - Built using React and Node.js
    """

    processor = NLPProcessor()
    result = processor.process_resume(sample_text)

    print("Extracted Information:")
    print(f"Name: {result['name']}")
    print(f"Email: {result['email']}")
    print(f"Phone: {result['phone']}")
    print(f"Skills: {', '.join(result['skills'])}")
    print(f"Keywords: {', '.join(result['keywords'][:10])}")
