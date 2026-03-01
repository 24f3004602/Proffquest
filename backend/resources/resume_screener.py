"""
ATS-Style Resume Screener for students and companies.
Analyzes resumes against job descriptions and provides scoring and feedback.
"""
from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity
from models import Student, Placement_drive, Application, Drive_eligibility
from utils.decorators import role_required
import json
import re


# Common skills categorized
SKILLS_DATABASE = {
    'programming_languages': [
        'python', 'java', 'javascript', 'c++', 'c#', 'c', 'ruby', 'go', 'rust',
        'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'typescript',
        'dart', 'objective-c', 'assembly', 'vba', 'groovy', 'lua'
    ],
    'web_technologies': [
        'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django',
        'flask', 'spring', 'asp.net', 'laravel', 'ruby on rails', 'nextjs',
        'gatsby', 'svelte', 'jquery', 'bootstrap', 'tailwind', 'sass', 'less',
        'webpack', 'babel', 'graphql', 'rest api', 'websocket'
    ],
    'databases': [
        'mysql', 'postgresql', 'mongodb', 'oracle', 'sql server', 'sqlite',
        'redis', 'elasticsearch', 'cassandra', 'dynamodb', 'firebase', 'neo4j',
        'mariadb', 'couchdb', 'influxdb'
    ],
    'cloud_devops': [
        'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'jenkins',
        'terraform', 'ansible', 'ci/cd', 'github actions', 'gitlab ci', 'circleci',
        'linux', 'unix', 'bash', 'powershell', 'nginx', 'apache', 'heroku',
        'cloudflare', 'vercel', 'netlify'
    ],
    'data_ml': [
        'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras',
        'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'tableau',
        'power bi', 'excel', 'data analysis', 'data visualization', 'nlp',
        'computer vision', 'opencv', 'spark', 'hadoop', 'airflow', 'dbt',
        'bigquery', 'snowflake', 'databricks'
    ],
    'mobile': [
        'android', 'ios', 'flutter', 'react native', 'xamarin', 'ionic',
        'swift', 'kotlin', 'objective-c', 'swiftui', 'jetpack compose'
    ],
    'soft_skills': [
        'leadership', 'communication', 'teamwork', 'problem solving',
        'analytical', 'creative', 'adaptable', 'time management',
        'project management', 'agile', 'scrum', 'collaboration'
    ],
    'tools': [
        'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'slack',
        'figma', 'sketch', 'adobe xd', 'photoshop', 'illustrator', 'vscode',
        'intellij', 'eclipse', 'postman', 'swagger'
    ]
}

# Education keywords and degrees
EDUCATION_LEVELS = {
    'phd': 100,
    'doctorate': 100,
    'masters': 80,
    'mtech': 80,
    'mba': 80,
    'ms': 80,
    'bachelors': 60,
    'btech': 60,
    'be': 60,
    'bsc': 60,
    'bca': 55,
    'diploma': 40,
}

# Experience level keywords
EXPERIENCE_KEYWORDS = {
    'intern': 0,
    'fresher': 0,
    'entry level': 0,
    'junior': 1,
    '1 year': 1,
    '2 years': 2,
    '3 years': 3,
    '4 years': 4,
    '5 years': 5,
    'senior': 5,
    'lead': 7,
    'principal': 8,
    'architect': 8,
    'manager': 6,
    'director': 10,
}


def extract_text_content(resume_url_or_text):
    """
    Extract text content from resume.
    For now, expects plain text or URL to text content.
    In production, you'd integrate with PDF/DOCX parsers.
    """
    if resume_url_or_text.startswith('http'):
        # In production, fetch and parse the document
        # For now, return empty to indicate URL-based resume
        return None
    return resume_url_or_text


def extract_skills(text):
    """Extract skills from text content."""
    text_lower = text.lower()
    found_skills = {category: [] for category in SKILLS_DATABASE}
    
    for category, skills in SKILLS_DATABASE.items():
        for skill in skills:
            # Use word boundary for more accurate matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills[category].append(skill)
    
    return found_skills


def extract_education_level(text):
    """Extract highest education level mentioned."""
    text_lower = text.lower()
    highest_score = 0
    highest_level = None
    
    for level, score in EDUCATION_LEVELS.items():
        if level in text_lower and score > highest_score:
            highest_score = score
            highest_level = level
    
    return highest_level, highest_score


def extract_experience_years(text):
    """Extract years of experience from text."""
    text_lower = text.lower()
    
    # Look for explicit year mentions
    year_patterns = [
        r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
        r'experience\s*[:of]*\s*(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s*exp',
    ]
    
    for pattern in year_patterns:
        match = re.search(pattern, text_lower)
        if match:
            return int(match.group(1))
    
    # Check for experience level keywords
    for keyword, years in EXPERIENCE_KEYWORDS.items():
        if keyword in text_lower:
            return years
    
    return 0


def extract_job_requirements(job_description):
    """Extract requirements from job description."""
    text_lower = job_description.lower()
    
    # Extract required skills
    required_skills = extract_skills(job_description)
    
    # Extract required experience
    required_experience = extract_experience_years(job_description)
    
    # Extract education requirements
    required_education, _ = extract_education_level(job_description)
    
    return {
        'skills': required_skills,
        'experience_years': required_experience,
        'education': required_education
    }


def calculate_ats_score(resume_data, job_requirements):
    """
    Calculate ATS score based on resume vs job requirements.
    Returns score (0-100) and detailed feedback.
    """
    score = 0
    feedback = []
    max_score = 100
    
    # Skills matching (60% weight)
    skills_score = 0
    skills_max = 60
    matched_skills = []
    missing_skills = []
    
    # Flatten job requirements skills
    required_skill_list = []
    for category_skills in job_requirements['skills'].values():
        required_skill_list.extend(category_skills)
    
    # Flatten resume skills
    resume_skill_list = []
    for category_skills in resume_data['skills'].values():
        resume_skill_list.extend(category_skills)
    
    if required_skill_list:
        for skill in required_skill_list:
            if skill in resume_skill_list:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)
        
        skills_match_ratio = len(matched_skills) / len(required_skill_list)
        skills_score = int(skills_match_ratio * skills_max)
    else:
        # No specific skills required, give partial credit
        skills_score = skills_max // 2 if resume_skill_list else 0
    
    score += skills_score
    
    # Skills feedback
    if matched_skills:
        feedback.append({
            'category': 'skills_matched',
            'type': 'positive',
            'message': f"Skills matched: {', '.join(matched_skills[:10])}"
        })
    if missing_skills:
        feedback.append({
            'category': 'skills_missing',
            'type': 'improvement',
            'message': f"Consider adding: {', '.join(missing_skills[:5])}"
        })
    
    # Experience matching (25% weight)
    exp_score = 0
    exp_max = 25
    required_exp = job_requirements.get('experience_years', 0)
    resume_exp = resume_data.get('experience_years', 0)
    
    if required_exp == 0:
        # Entry level position
        exp_score = exp_max
        feedback.append({
            'category': 'experience',
            'type': 'positive',
            'message': "Entry-level position - no experience requirement"
        })
    elif resume_exp >= required_exp:
        exp_score = exp_max
        feedback.append({
            'category': 'experience',
            'type': 'positive',
            'message': f"Experience meets requirement ({resume_exp}+ years)"
        })
    else:
        exp_ratio = resume_exp / required_exp if required_exp > 0 else 0
        exp_score = int(exp_ratio * exp_max)
        feedback.append({
            'category': 'experience',
            'type': 'warning' if exp_ratio >= 0.5 else 'negative',
            'message': f"Experience gap: {required_exp - resume_exp} more years preferred"
        })
    
    score += exp_score
    
    # Education matching (15% weight)
    edu_score = 0
    edu_max = 15
    required_edu = job_requirements.get('education')
    resume_edu = resume_data.get('education')
    
    if required_edu is None:
        edu_score = edu_max
    elif resume_edu is None:
        feedback.append({
            'category': 'education',
            'type': 'improvement',
            'message': "Add education details to your resume"
        })
    else:
        resume_edu_score = EDUCATION_LEVELS.get(resume_edu, 0)
        required_edu_score = EDUCATION_LEVELS.get(required_edu, 0)
        
        if resume_edu_score >= required_edu_score:
            edu_score = edu_max
            feedback.append({
                'category': 'education',
                'type': 'positive',
                'message': f"Education meets requirement ({resume_edu.upper()})"
            })
        else:
            edu_ratio = resume_edu_score / required_edu_score if required_edu_score > 0 else 0
            edu_score = int(edu_ratio * edu_max)
            feedback.append({
                'category': 'education',
                'type': 'warning',
                'message': f"Preferred education: {required_edu.upper()}"
            })
    
    score += edu_score
    
    # Additional resume quality checks
    additional_feedback = []
    
    # Check for diverse skill categories
    skill_categories_found = sum(1 for skills in resume_data['skills'].values() if skills)
    if skill_categories_found >= 4:
        additional_feedback.append({
            'category': 'diversity',
            'type': 'positive',
            'message': "Good skill diversity across multiple areas"
        })
    elif skill_categories_found <= 1:
        additional_feedback.append({
            'category': 'diversity',
            'type': 'improvement',
            'message': "Consider showcasing more skill areas"
        })
    
    # Calculate grade
    if score >= 90:
        grade = 'A+'
        grade_message = "Excellent match! Highly recommended for this position."
    elif score >= 80:
        grade = 'A'
        grade_message = "Strong match! Good candidate for this position."
    elif score >= 70:
        grade = 'B+'
        grade_message = "Good match with some areas for improvement."
    elif score >= 60:
        grade = 'B'
        grade_message = "Moderate match. Consider strengthening relevant skills."
    elif score >= 50:
        grade = 'C'
        grade_message = "Partial match. Significant skill gaps to address."
    else:
        grade = 'D'
        grade_message = "Limited match. May need more experience or skills."
    
    return {
        'score': score,
        'grade': grade,
        'grade_message': grade_message,
        'breakdown': {
            'skills': {'score': skills_score, 'max': skills_max},
            'experience': {'score': exp_score, 'max': exp_max},
            'education': {'score': edu_score, 'max': edu_max}
        },
        'feedback': feedback + additional_feedback,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills[:10]
    }


class ATSResumeScreener(Resource):
    """Public ATS Resume Screener - can be used without authentication."""
    
    def post(self):
        """
        Screen a resume against a job description.
        
        Body:
        {
            "resume_text": "...",  # Resume content as plain text
            "job_description": "...",  # Job description to match against
            "job_title": "..." (optional)
        }
        """
        data = request.get_json()
        
        if not data:
            return {'message': 'Request body required'}, 400
        
        resume_text = data.get('resume_text', '').strip()
        job_description = data.get('job_description', '').strip()
        job_title = data.get('job_title', '')
        
        if not resume_text:
            return {'message': 'resume_text is required'}, 400
        
        if not job_description:
            return {'message': 'job_description is required'}, 400
        
        # Analyze resume
        resume_data = {
            'skills': extract_skills(resume_text),
            'experience_years': extract_experience_years(resume_text),
            'education': extract_education_level(resume_text)[0]
        }
        
        # Extract job requirements
        job_requirements = extract_job_requirements(job_description)
        
        # Calculate ATS score
        result = calculate_ats_score(resume_data, job_requirements)
        
        # Add resume analysis summary
        all_resume_skills = []
        for skills in resume_data['skills'].values():
            all_resume_skills.extend(skills)
        
        result['resume_analysis'] = {
            'total_skills_found': len(all_resume_skills),
            'skills_by_category': {k: len(v) for k, v in resume_data['skills'].items()},
            'experience_years': resume_data['experience_years'],
            'education_level': resume_data['education']
        }
        
        if job_title:
            result['job_title'] = job_title
        
        return result, 200


class ATSStudentResumeCheck(Resource):
    """ATS Check against a specific drive for authenticated students."""
    
    @role_required('student')
    def post(self, drive_id):
        """
        Check student's resume against a specific placement drive.
        """
        identity = json.loads(get_jwt_identity())
        student_id = identity['id']
        
        # Get student
        student = Student.query.get_or_404(student_id)
        
        # Get drive
        drive = Placement_drive.query.get_or_404(drive_id)
        
        if not drive.is_approved:
            return {'message': 'Drive not available'}, 404
        
        data = request.get_json() or {}
        resume_text = data.get('resume_text', '').strip()
        
        if not resume_text:
            return {'message': 'resume_text is required. Please paste your resume content.'}, 400
        
        # Build job description from drive details
        job_description = f"""
        Job Title: {drive.job_title}
        Description: {drive.job_description or ''}
        Location: {drive.location or ''}
        Package: {drive.package_offered or ''}
        """
        
        # Add eligibility criteria if available
        eligibilities = Drive_eligibility.query.filter_by(drive_id=drive.id).all()
        for elig in eligibilities:
            if elig.additional_criteria:
                job_description += f"\nAdditional Requirements: {elig.additional_criteria}"
        
        # Analyze resume
        resume_data = {
            'skills': extract_skills(resume_text),
            'experience_years': extract_experience_years(resume_text),
            'education': extract_education_level(resume_text)[0]
        }
        
        # Extract job requirements
        job_requirements = extract_job_requirements(job_description)
        
        # Calculate ATS score
        result = calculate_ats_score(resume_data, job_requirements)
        
        # Add context
        result['drive'] = {
            'id': drive.id,
            'job_title': drive.job_title,
            'company_name': drive.company.company_name,
            'package_offered': drive.package_offered
        }
        
        # Add eligibility check
        eligible = True
        eligibility_feedback = []
        
        for elig in eligibilities:
            if elig.branch and student.branch.lower() != elig.branch.lower():
                if not any(b.lower() == student.branch.lower() for b in elig.branch.split(',')):
                    eligible = False
                    eligibility_feedback.append(f"Branch requirement: {elig.branch}")
            
            if elig.min_cgpa and student.cgpa < elig.min_cgpa:
                eligible = False
                eligibility_feedback.append(f"CGPA requirement: {elig.min_cgpa} (yours: {student.cgpa})")
            
            if elig.passing_year and student.year != elig.passing_year:
                eligibility_feedback.append(f"Preferred batch: {elig.passing_year}")
        
        result['eligibility'] = {
            'eligible': eligible,
            'feedback': eligibility_feedback
        }
        
        return result, 200


class ATSCompanyBulkScreen(Resource):
    """Bulk ATS screening for companies to filter applicants."""
    
    @role_required('company')
    def post(self, drive_id):
        """
        Bulk screen all applicants for a drive.
        Returns ranked list of applicants with ATS scores.
        """
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        
        # Get drive and verify ownership
        drive = Placement_drive.query.get_or_404(drive_id)
        if drive.company_id != company_id:
            return {'message': 'Access denied'}, 403
        
        # Get all applications for this drive
        applications = Application.query.filter_by(drive_id=drive_id).all()
        
        if not applications:
            return {'message': 'No applications found', 'results': []}, 200
        
        # Build job description
        job_description = f"""
        Job Title: {drive.job_title}
        Description: {drive.job_description or ''}
        """
        
        # Get job requirements
        job_requirements = extract_job_requirements(job_description)
        
        results = []
        data = request.get_json() or {}
        
        for app in applications:
            student = Student.query.get(app.student_id)
            if not student:
                continue
            
            # Check if resume text was provided for this application
            # In practice, this could come from stored resume or the request body
            resume_text = data.get('resumes', {}).get(str(app.id), '')
            
            if resume_text:
                resume_data = {
                    'skills': extract_skills(resume_text),
                    'experience_years': extract_experience_years(resume_text),
                    'education': extract_education_level(resume_text)[0]
                }
                ats_result = calculate_ats_score(resume_data, job_requirements)
            else:
                # Basic scoring without resume content
                ats_result = {
                    'score': None,
                    'grade': 'N/A',
                    'grade_message': 'Resume content not available for analysis'
                }
            
            results.append({
                'application_id': app.id,
                'student': {
                    'id': student.id,
                    'full_name': student.full_name,
                    'email': student.email,
                    'branch': student.branch,
                    'cgpa': student.cgpa,
                    'year': student.year
                },
                'status': app.status,
                'applied_at': app.applied_at.isoformat() if app.applied_at else None,
                'ats_score': ats_result.get('score'),
                'ats_grade': ats_result.get('grade'),
                'matched_skills': ats_result.get('matched_skills', []),
                'missing_skills': ats_result.get('missing_skills', [])
            })
        
        # Sort by ATS score (None scores at the end)
        results.sort(key=lambda x: (x['ats_score'] is not None, x['ats_score'] or 0), reverse=True)
        
        return {
            'drive': {
                'id': drive.id,
                'job_title': drive.job_title,
                'total_applicants': len(applications)
            },
            'results': results
        }, 200


class ATSSkillsAnalyzer(Resource):
    """Analyze skills from text - useful for both students and companies."""
    
    def post(self):
        """
        Extract and categorize skills from text.
        
        Body: {"text": "..."}
        """
        data = request.get_json()
        
        if not data or not data.get('text'):
            return {'message': 'text is required'}, 400
        
        text = data['text']
        skills = extract_skills(text)
        experience = extract_experience_years(text)
        education, edu_score = extract_education_level(text)
        
        # Count total skills
        all_skills = []
        for category_skills in skills.values():
            all_skills.extend(category_skills)
        
        return {
            'skills': skills,
            'skills_summary': {
                'total': len(all_skills),
                'by_category': {k: len(v) for k, v in skills.items()}
            },
            'experience_years': experience,
            'education': {
                'level': education,
                'score': edu_score
            },
            'top_skills': all_skills[:20]
        }, 200
