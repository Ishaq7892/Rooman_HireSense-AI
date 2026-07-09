from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ParsedDocument(BaseModel):
    file_name: str = Field(..., description="Name of the uploaded file")
    file_type: str = Field(..., description="File type: pdf, docx, or txt")
    raw_text: str = Field(..., description="Raw extracted text from the document")
    parsed_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when document was parsed")


class UploadResponse(BaseModel):
    document_id: str = Field(..., description="Unique identifier for the uploaded document")
    parsed_document: ParsedDocument = Field(..., description="Parsed document data")
    message: str = Field(default="Document uploaded and parsed successfully", description="Success message")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")


# ------------------------------
# Structured Data Models
# ------------------------------

class ExperienceItem(BaseModel):
    job_title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    start_date: Optional[str] = Field(None, description="Start date (e.g., Jan 2020)")
    end_date: Optional[str] = Field(None, description="End date (e.g., Present or Dec 2023)")
    description: Optional[str] = Field(None, description="Job responsibilities and achievements")


class EducationItem(BaseModel):
    degree: str = Field(..., description="Degree obtained")
    school: str = Field(..., description="School/university name")
    location: Optional[str] = Field(None, description="School location")
    start_date: Optional[str] = Field(None, description="Start date")
    end_date: Optional[str] = Field(None, description="End date")
    description: Optional[str] = Field(None, description="Relevant coursework or achievements")


class ProjectItem(BaseModel):
    title: str = Field(..., description="Project title")
    description: Optional[str] = Field(None, description="Project description")
    technologies: Optional[List[str]] = Field(default_factory=list, description="Technologies used")
    link: Optional[str] = Field(None, description="Project link (if any)")


class CertificationItem(BaseModel):
    name: str = Field(..., description="Certification name")
    issuer: str = Field(..., description="Certification issuer (e.g., Google, AWS)")
    date: Optional[str] = Field(None, description="Certification date")
    link: Optional[str] = Field(None, description="Certification link (if any)")


class StructuredResume(BaseModel):
    name: str = Field(..., description="Candidate's full name")
    email: Optional[str] = Field(None, description="Candidate's email address")
    phone: Optional[str] = Field(None, description="Candidate's phone number")
    skills: List[str] = Field(default_factory=list, description="List of skills")
    experience: List[ExperienceItem] = Field(default_factory=list, description="Work experience")
    education: List[EducationItem] = Field(default_factory=list, description="Education history")
    projects: List[ProjectItem] = Field(default_factory=list, description="Projects")
    certifications: List[CertificationItem] = Field(default_factory=list, description="Certifications")


class StructuredJobDescription(BaseModel):
    job_title: str = Field(..., description="Job title")
    company: Optional[str] = Field(None, description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    required_skills: List[str] = Field(default_factory=list, description="Required skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred skills")
    responsibilities: List[str] = Field(default_factory=list, description="Job responsibilities")
    requirements: List[str] = Field(default_factory=list, description="Job requirements")
    experience_required: Optional[str] = Field(None, description="Experience required")
    education_required: Optional[str] = Field(None, description="Education required")
    technologies: List[str] = Field(default_factory=list, description="Technologies/tools used in the role")


class ExtractionResponse(BaseModel):
    document_id: str = Field(..., description="Document ID")
    structured_data: StructuredResume | StructuredJobDescription = Field(..., description="Extracted structured data")


# ------------------------------
# ATS Scoring Models
# ------------------------------

class ATSScoreBreakdown(BaseModel):
    skill_match_score: float = Field(..., description="Skill match score (0-100) - 40% of total")
    experience_score: float = Field(..., description="Experience score (0-100) - 25% of total")
    education_score: float = Field(..., description="Education score (0-100) - 15% of total")
    project_match_score: float = Field(..., description="Project match score (0-100) - 10% of total")
    certification_score: float = Field(..., description="Certification score (0-100) - 10% of total")


class ATSResult(BaseModel):
    total_score: float = Field(..., description="Total ATS score (0-100)")
    score_breakdown: ATSScoreBreakdown = Field(..., description="Detailed score breakdown")
    reasoning: str = Field(..., description="Overall reasoning for the score")
    strengths: List[str] = Field(default_factory=list, description="List of candidate's strengths")
    weaknesses: List[str] = Field(default_factory=list, description="List of candidate's weaknesses")
    missing_skills: List[str] = Field(default_factory=list, description="List of skills required by the job that the candidate is missing")


class ATSRequest(BaseModel):
    resume_structured: StructuredResume = Field(..., description="Structured resume data")
    jd_structured: StructuredJobDescription = Field(..., description="Structured job description data")


# ------------------------------
# Candidate Ranking Models
# ------------------------------

class CandidateData(BaseModel):
    document_id: str = Field(..., description="Unique identifier for the candidate's resume")
    raw_text: str = Field(..., description="Raw text from the resume")
    structured_data: StructuredResume = Field(..., description="Structured resume data")


class RankedCandidate(BaseModel):
    rank: int = Field(..., description="Candidate's rank (1 = top candidate)")
    candidate_name: Optional[str] = Field(None, description="Candidate's name")
    document_id: str = Field(..., description="Document ID of the resume")
    ats_score: float = Field(..., description="ATS score (0-100)")
    similarity_score: float = Field(..., description="Cosine similarity score (0-100)")
    combined_score: float = Field(..., description="Combined score (weighted average)")
    reasoning: str = Field(..., description="Reasoning for the score")
    strengths: List[str] = Field(default_factory=list, description="Candidate's strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Candidate's weaknesses")
    missing_skills: List[str] = Field(default_factory=list, description="Missing required skills")


class RankingRequest(BaseModel):
    job_description_data: StructuredJobDescription = Field(..., description="Structured job description data")
    job_description_raw_text: str = Field(..., description="Raw text from the job description")
    candidates: List[CandidateData] = Field(..., description="List of candidate data")
    ats_weight: float = Field(0.6, description="Weight for ATS score (0-1, default 0.6)")
    similarity_weight: float = Field(0.4, description="Weight for similarity score (0-1, default 0.4)")


class RankingResponse(BaseModel):
    ranked_candidates: List[RankedCandidate] = Field(..., description="List of ranked candidates")
    top_candidate: Optional[RankedCandidate] = Field(None, description="Top candidate")
    total_candidates: int = Field(..., description="Total number of candidates ranked")
    ats_weight: float = Field(..., description="Weight used for ATS score")
    similarity_weight: float = Field(..., description="Weight used for similarity score")


# ------------------------------
# Interview Question Generator Models
# ------------------------------

class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class InterviewQuestion(BaseModel):
    question: str = Field(..., description="Interview question")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level of the question")
    category: str = Field(..., description="Category of the question (Missing Skills, Experience, Projects)")
    context: Optional[str] = Field(None, description="Context or explanation for why this question is asked")


class InterviewQuestionRequest(BaseModel):
    candidate_name: Optional[str] = Field(None, description="Candidate's name")
    structured_resume: StructuredResume = Field(..., description="Structured resume data")
    structured_job_description: StructuredJobDescription = Field(..., description="Structured job description data")
    missing_skills: Optional[List[str]] = Field(default_factory=list, description="List of missing skills")
    difficulty_distribution: Optional[dict] = Field(
        None, 
        description="How many questions for each difficulty (e.g., {'Easy': 2, 'Medium': 2, 'Hard': 1})"
    )


class InterviewQuestionResponse(BaseModel):
    candidate_name: Optional[str] = Field(None, description="Candidate's name")
    total_questions: int = Field(..., description="Total number of interview questions generated")
    questions: List[InterviewQuestion] = Field(..., description="List of interview questions")
