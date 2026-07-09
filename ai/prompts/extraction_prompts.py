from langchain.prompts import PromptTemplate

# ------------------------------
# Resume Extraction Prompt
# ------------------------------
RESUME_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["text"],
    template="""
You are an expert resume parser. Your task is to extract structured information from the following resume text.

Please extract the following information in JSON format:
- name: Full name of the candidate
- email: Email address (if present)
- phone: Phone number (if present)
- skills: List of skills (technical and soft skills)
- experience: List of work experiences, each with:
  - job_title: Job title
  - company: Company name
  - location: Job location (if present)
  - start_date: Start date (if present)
  - end_date: End date (if present, use "Present" if current)
  - description: Job responsibilities and achievements (if present)
- education: List of education entries, each with:
  - degree: Degree obtained
  - school: School/university name
  - location: School location (if present)
  - start_date: Start date (if present)
  - end_date: End date (if present)
  - description: Relevant coursework or achievements (if present)
- projects: List of projects, each with:
  - title: Project title
  - description: Project description (if present)
  - technologies: List of technologies used (if present)
  - link: Project link (if present)
- certifications: List of certifications, each with:
  - name: Certification name
  - issuer: Certification issuer
  - date: Certification date (if present)
  - link: Certification link (if present)

Resume Text:
{text}

Return ONLY the JSON output, no additional text.
"""
)

# ------------------------------
# Job Description Extraction Prompt
# ------------------------------
JD_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["text"],
    template="""
You are an expert job description parser. Your task is to extract structured information from the following job description.

Please extract the following information in JSON format:
- job_title: Job title
- company: Company name (if present)
- location: Job location (if present)
- required_skills: List of required skills
- preferred_skills: List of preferred skills (if any)
- responsibilities: List of key responsibilities
- requirements: List of job requirements
- experience_required: Required experience (if present)
- education_required: Required education (if present)
- technologies: List of technologies/tools used in the role (if any)

Job Description Text:
{text}

Return ONLY the JSON output, no additional text.
"""
)

# ------------------------------
# ATS Reasoning Prompt
# ------------------------------
ATS_REASONING_PROMPT = PromptTemplate(
    input_variables=["resume_data", "jd_data", "score_breakdown"],
    template="""
You are HireSense AI, an expert AI Technical Recruiter and ATS (Applicant Tracking System). 
Your task is to evaluate a candidate's resume against the provided Job Description and return the required analysis using semantic understanding, not simple keyword matching.

Job Description Data:
{jd_data}

Resume Data:
{resume_data}

Score Breakdown (0-100):
{score_breakdown}

Please provide a detailed analysis in JSON format with the following fields (only these fields, no extra):
- reasoning: A 2-3 sentence overall reasoning explaining the score, referencing the score breakdown
- strengths: A list of 2-4 key strengths of the candidate (e.g., relevant skills, experience, projects, certifications)
- weaknesses: A list of 1-3 key weaknesses or areas for improvement
- missing_skills: A list of skills from the job description's required_skills and technologies that are not present in the candidate's skills

Use semantic understanding instead of exact keyword matching when evaluating skills and experience.

Return ONLY the JSON output, no additional text.
"""
)

# ------------------------------
# Interview Question Generator Prompt
# ------------------------------
INTERVIEW_QUESTION_PROMPT = PromptTemplate(
    input_variables=["candidate_name", "resume_data", "jd_data", "missing_skills", "difficulty_distribution"],
    template="""
You are an expert interviewer for a tech company. Your task is to generate 5 interview questions for a candidate based on their resume, the job description, and their missing skills.

Here is the information you need:
- Candidate Name: {candidate_name}
- Job Description Data: {jd_data}
- Resume Data: {resume_data}
- Missing Skills: {missing_skills}
- Difficulty Distribution: {difficulty_distribution} (how many questions for each difficulty level)

Please generate exactly 5 interview questions that cover the following categories:
1. Missing Skills (questions about the skills the candidate is missing)
2. Experience (questions about the candidate's work experience)
3. Projects (questions about the candidate's projects)

Please return the questions in JSON format with the following structure for each question:
- question: The interview question text
- difficulty: "Easy", "Medium", or "Hard"
- category: "Missing Skills", "Experience", or "Projects"
- context: Brief explanation of why this question is relevant

Make sure the questions are tailored specifically to the candidate and the job description.

Return ONLY the JSON output as a list of questions, no additional text.
"""
)
