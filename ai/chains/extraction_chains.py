import json
import re
from typing import List
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from backend.core.config import settings
from backend.core.logging import logger
from ai.prompts import RESUME_EXTRACTION_PROMPT, JD_EXTRACTION_PROMPT, ATS_REASONING_PROMPT, INTERVIEW_QUESTION_PROMPT
from backend.models.schemas import StructuredResume, StructuredJobDescription


class ExtractionChains:
    """
    LangChain chains for extracting structured data from resumes and job descriptions,
    generating ATS reasoning, and generating interview questions.
    """

    def __init__(self):
        # Initialize LLM with Groq only if API key is available
        self.llm = None
        if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_api_key_here":
            try:
                self.llm = ChatGroq(
                    model=settings.GROQ_MODEL_NAME,
                    temperature=0.7,
                    groq_api_key=settings.GROQ_API_KEY
                )
                logger.info("ExtractionChains initialized with Groq LLM")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq LLM: {str(e)}. Using fallback extraction.")
        else:
            logger.warning("GROQ_API_KEY not set. Using fallback extraction.")
        
        # Initialize output parsers
        self.resume_parser = JsonOutputParser(pydantic_object=StructuredResume)
        self.jd_parser = JsonOutputParser(pydantic_object=StructuredJobDescription)
        
        # Create chains only if LLM is available
        self.resume_chain = None
        self.jd_chain = None
        self.ats_reasoning_chain = None
        self.interview_question_chain = None
        
        if self.llm:
            self.resume_chain = LLMChain(
                llm=self.llm,
                prompt=RESUME_EXTRACTION_PROMPT,
                output_parser=self.resume_parser
            )
            
            self.jd_chain = LLMChain(
                llm=self.llm,
                prompt=JD_EXTRACTION_PROMPT,
                output_parser=self.jd_parser
            )
            
            self.ats_reasoning_chain = LLMChain(
                llm=self.llm,
                prompt=ATS_REASONING_PROMPT,
                output_parser=JsonOutputParser()
            )
            
            self.interview_question_chain = LLMChain(
                llm=self.llm,
                prompt=INTERVIEW_QUESTION_PROMPT,
                output_parser=JsonOutputParser()
            )
        
        logger.info("ExtractionChains initialized successfully")
        
    def _extract_skills_fallback(self, text: str) -> List[str]:
        """Fallback skill extraction using regex and keyword matching."""
        common_skills = [
            "python", "java", "javascript", "typescript", "react", "angular", "vue",
            "node.js", "express", "django", "flask", "fastapi", "spring",
            "sql", "mysql", "postgresql", "mongodb", "redis",
            "aws", "azure", "gcp", "docker", "kubernetes",
            "git", "github", "gitlab", "ci/cd", "jenkins",
            "machine learning", "ml", "deep learning", "dl", "nlp",
            "data science", "data analysis", "pandas", "numpy",
            "tensorflow", "pytorch", "scikit-learn",
            "html", "css", "sass", "less", "bootstrap",
            "c++", "c#", "ruby", "go", "rust", "php"
        ]
        skills = []
        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text.lower()):
                skills.append(skill.title())
        return list(set(skills))[:20]
    
    def _extract_name_fallback(self, text: str) -> str:
        """Fallback name extraction (first 2 lines of text)."""
        lines = text.splitlines()
        for line in lines[:5]:
            clean_line = line.strip()
            forbidden_chars = ('@', 'http', 'www')
            if clean_line and len(clean_line.split()) <= 4 and not any((char in clean_line for char in forbidden_chars)):
                return clean_line
        return "Candidate"
    
    def _extract_email_fallback(self, text: str) -> str:
        """Fallback email extraction using regex."""
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        return email_match.group() if email_match else "candidate@example.com"
    
    def _extract_phone_fallback(self, text: str) -> str:
        """Fallback phone number extraction using regex."""
        # Match common phone number formats
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        return phone_match.group() if phone_match else "+1-555-123-4567"
    
    def _extract_section_fallback(self, text: str, section_headers: List[str]) -> List[dict]:
        """Fallback section extraction (for experience, education, projects)."""
        sections = []
        lines = text.splitlines()
        current_section = None
        current_lines = []
        
        # Normalize section headers for matching
        section_headers_lower = [h.lower() for h in section_headers]
        
        # Define all possible headers to detect boundaries and avoid leaking subsequent sections
        boundary_headers = [
            "experience", "work experience", "employment history", "professional experience", "internship", "work history",
            "education", "academic background", "qualifications", "academic profile", "education history",
            "projects", "personal projects", "side projects", "key projects", "academic projects",
            "certifications", "licenses", "courses",
            "skills", "technical skills", "core skills", "languages", "hobbies", "interests", 
            "summary", "profile", "about me", "contact"
        ]
        
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            
            # Check if this line is any section header boundary
            is_boundary = False
            matched_header = None
            for bh in boundary_headers:
                if bh == line_lower or (bh in line_lower and len(line_lower.split()) < 6):
                    is_boundary = True
                    matched_header = bh
                    break
            
            if is_boundary:
                # If we hit a boundary, save the current target section we were collecting
                if current_section and current_lines:
                    sections.append({
                        "raw_content": "\n".join(current_lines).strip()
                    })
                    current_lines = []
                
                # Check if this boundary header is one of the target headers we want to extract
                is_target = False
                for target_h in section_headers_lower:
                    if target_h in matched_header or matched_header in target_h:
                        is_target = True
                        break
                
                if is_target:
                    current_section = matched_header
                else:
                    current_section = None
            else:
                # If we are currently inside a target section, collect the line
                if current_section:
                    if line.strip():
                        current_lines.append(line.strip())
        
        # Add the last section if it was a target section
        if current_section and current_lines:
            sections.append({
                "raw_content": "\n".join(current_lines).strip()
            })
        
        return sections
    
    def _extract_experience_fallback(self, text: str) -> List[dict]:
        """Fallback experience extraction."""
        raw_sections = self._extract_section_fallback(text, ["experience", "work experience", "employment history", "professional experience", "internship", "work history"])
        experience_list = []
        
        for section in raw_sections:
            # Try to extract job title and company (simple approach)
            content = section["raw_content"]
            lines = content.splitlines()
            
            if lines:
                # First line might be job title and company
                job_title = lines[0]
                company = "Company"
                
                # Look for keywords like "at" or " - " to split job title and company
                if " at " in job_title.lower():
                    parts = job_title.split(" at ", 1)
                    job_title = parts[0].strip()
                    company = parts[1].strip()
                elif " - " in job_title:
                    parts = job_title.split(" - ", 1)
                    job_title = parts[0].strip()
                    company = parts[1].strip()
                
                experience_list.append({
                    "job_title": job_title,
                    "company": company,
                    "location": "",
                    "description": "\n".join(lines[1:]) if len(lines) > 1 else ""
                })
        
        return experience_list[:10]
    
    def _extract_education_fallback(self, text: str) -> List[dict]:
        """Fallback education extraction."""
        raw_sections = self._extract_section_fallback(text, ["education", "academic background", "qualifications"])
        education_list = []
        
        for section in raw_sections:
            content = section["raw_content"]
            lines = content.splitlines()
            
            if lines:
                education_list.append({
                    "degree": lines[0],
                    "school": "University",
                    "description": "\n".join(lines[1:]) if len(lines) > 1 else ""
                })
        
        return education_list[:10]
    
    def _extract_projects_fallback(self, text: str) -> List[dict]:
        """Fallback project extraction."""
        raw_sections = self._extract_section_fallback(text, ["projects", "personal projects", "side projects", "key projects"])
        project_list = []
        
        for section in raw_sections:
            content = section["raw_content"]
            lines = content.splitlines()
            
            if lines:
                project_list.append({
                    "title": lines[0],
                    "description": "\n".join(lines[1:]) if len(lines) > 1 else "",
                    "technologies": self._extract_skills_fallback(content)
                })
        
        return project_list[:10]

    def extract_resume(self, text: str) -> StructuredResume:
        """
        Extract structured data from a resume.

        Args:
            text: Raw text from the resume

        Returns:
            StructuredResume object with extracted data
        """
        try:
            if self.llm and self.resume_chain:
                logger.info("Starting resume extraction with LLM")
                result = self.resume_chain.run(text=text)
                logger.info("Resume extraction completed successfully")
                
                if isinstance(result, list):
                    logger.warning(f"Resume extraction returned a list instead of a dict. Taking the first element. List contents: {result}")
                    if result:
                        result = result[0]
                    else:
                        result = {}
                elif isinstance(result, StructuredResume):
                    return result
                
                sanitized_result = self._sanitize_resume_dict(result)
                return StructuredResume(**sanitized_result)
            else:
                logger.info("Using fallback resume extraction")
                return StructuredResume(
                    name=self._extract_name_fallback(text),
                    email=self._extract_email_fallback(text),
                    phone=self._extract_phone_fallback(text),
                    skills=self._extract_skills_fallback(text),
                    experience=self._extract_experience_fallback(text),
                    education=self._extract_education_fallback(text),
                    projects=self._extract_projects_fallback(text),
                    certifications=[]
                )
        except Exception as e:
            logger.error(f"Error extracting resume data: {str(e)}", exc_info=True)
            if self.llm:
                raise Exception(f"LLM resume extraction failed: {str(e)}")
            logger.info("Falling back to basic resume extraction")
            return StructuredResume(
                name=self._extract_name_fallback(text),
                email=self._extract_email_fallback(text),
                phone=self._extract_phone_fallback(text),
                skills=self._extract_skills_fallback(text),
                experience=self._extract_experience_fallback(text),
                education=self._extract_education_fallback(text),
                projects=self._extract_projects_fallback(text),
                certifications=[]
            )

    def extract_job_description(self, text: str) -> StructuredJobDescription:
        """
        Extract structured data from a job description.

        Args:
            text: Raw text from the job description

        Returns:
            StructuredJobDescription object with extracted data
        """
        try:
            if self.llm and self.jd_chain:
                logger.info("Starting job description extraction with LLM")
                result = self.jd_chain.run(text=text)
                logger.info("Job description extraction completed successfully")
                
                if isinstance(result, list):
                    logger.warning(f"Job description extraction returned a list instead of a dict. Taking the first element. List contents: {result}")
                    if result:
                        result = result[0]
                    else:
                        result = {}
                elif isinstance(result, StructuredJobDescription):
                    return result
                
                sanitized_result = self._sanitize_jd_dict(result)
                return StructuredJobDescription(**sanitized_result)
            else:
                logger.info("Using fallback job description extraction")
                return StructuredJobDescription(
                    job_title="Software Engineer",
                    company="Company Inc.",
                    location="Remote",
                    required_skills=self._extract_skills_fallback(text),
                    preferred_skills=[],
                    responsibilities=[],
                    qualifications=[],
                    technologies=self._extract_skills_fallback(text)
                )
        except Exception as e:
            logger.error(f"Error extracting job description data: {str(e)}", exc_info=True)
            if self.llm:
                raise Exception(f"LLM job description extraction failed: {str(e)}")
            logger.info("Falling back to basic job description extraction")
            return StructuredJobDescription(
                job_title="Software Engineer",
                company="Company Inc.",
                location="Remote",
                required_skills=self._extract_skills_fallback(text),
                preferred_skills=[],
                responsibilities=[],
                qualifications=[],
                technologies=self._extract_skills_fallback(text)
            )
            
    def generate_ats_reasoning(self, resume_data: dict, jd_data: dict, score_breakdown: dict) -> dict:
        """
        Generate ATS reasoning, strengths, weaknesses, and missing skills using LLM.

        Args:
            resume_data: Structured resume data as dict
            jd_data: Structured job description data as dict
            score_breakdown: Score breakdown as dict

        Returns:
            Dict with reasoning, strengths, weaknesses, missing_skills
        """
        try:
            logger.info("Starting ATS reasoning generation")
            result = self.ats_reasoning_chain.run(
                resume_data=json.dumps(resume_data, indent=2),
                jd_data=json.dumps(jd_data, indent=2),
                score_breakdown=json.dumps(score_breakdown, indent=2)
            )
            logger.info("ATS reasoning generation completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error generating ATS reasoning: {str(e)}", exc_info=True)
            if self.llm:
                raise Exception(f"LLM ATS reasoning generation failed: {str(e)}")
            # Fallback to simple reasoning if LLM fails and LLM is not configured
            return {
                "reasoning": "Score calculated based on skill, experience, education, project, and certification match.",
                "strengths": [],
                "weaknesses": [],
                "missing_skills": []
            }
            
    def generate_interview_questions(
        self, 
        candidate_name: str, 
        resume_data: dict, 
        jd_data: dict, 
        missing_skills: list, 
        difficulty_distribution: dict
    ) -> list:
        """
        Generate interview questions using LLM.

        Args:
            candidate_name: Name of the candidate
            resume_data: Structured resume data as dict
            jd_data: Structured job description data as dict
            missing_skills: List of missing skills
            difficulty_distribution: How many questions for each difficulty

        Returns:
            List of interview question dicts
        """
        try:
            logger.info("Starting interview question generation")
            result = self.interview_question_chain.run(
                candidate_name=candidate_name,
                resume_data=json.dumps(resume_data, indent=2),
                jd_data=json.dumps(jd_data, indent=2),
                missing_skills=json.dumps(missing_skills, indent=2),
                difficulty_distribution=json.dumps(difficulty_distribution, indent=2)
            )
            logger.info("Interview question generation completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error generating interview questions: {str(e)}", exc_info=True)
            # Fallback to simple questions if LLM fails
            return [
                {
                    "question": "Tell me about yourself and your relevant experience.",
                    "difficulty": "Easy",
                    "category": "Experience",
                    "context": "General background question to start the interview."
                }
            ]

    def _flatten_to_list_of_strings(self, val) -> List[str]:
        if val is None:
            return []
        if isinstance(val, list):
            res = []
            for item in val:
                if isinstance(item, list):
                    res.extend(self._flatten_to_list_of_strings(item))
                elif isinstance(item, dict):
                    res.extend(self._flatten_to_list_of_strings(list(item.values())))
                else:
                    res.append(str(item))
            return res
        if isinstance(val, dict):
            res = []
            for k, v in val.items():
                res.extend(self._flatten_to_list_of_strings(v))
            return res
        if isinstance(val, str):
            if "," in val:
                return [s.strip() for s in val.split(",") if s.strip()]
            elif "\n" in val:
                return [s.strip() for s in val.split("\n") if s.strip()]
            else:
                return [val.strip()]
        return [str(val)]

    def _flatten_to_string(self, val) -> str:
        if val is None:
            return ""
        if isinstance(val, list):
            flat_items = []
            for item in val:
                flat_items.append(self._flatten_to_string(item))
            return "\n".join([x for x in flat_items if x])
        if isinstance(val, dict):
            flat_items = []
            for k, v in val.items():
                flat_items.append(f"{k}: {self._flatten_to_string(v)}")
            return "\n".join(flat_items)
        return str(val)

    def _sanitize_resume_dict(self, result: dict) -> dict:
        if not isinstance(result, dict):
            return {}
            
        # Standardize experience
        if "experience" in result and isinstance(result["experience"], list):
            for exp in result["experience"]:
                if isinstance(exp, dict) and "description" in exp:
                    exp["description"] = self._flatten_to_string(exp["description"])
                        
        # Standardize education
        if "education" in result and isinstance(result["education"], list):
            for edu in result["education"]:
                if isinstance(edu, dict) and "description" in edu:
                    edu["description"] = self._flatten_to_string(edu["description"])

        # Standardize projects
        if "projects" in result and isinstance(result["projects"], list):
            for proj in result["projects"]:
                if isinstance(proj, dict):
                    if "description" in proj:
                        proj["description"] = self._flatten_to_string(proj["description"])
                    if "technologies" in proj:
                        proj["technologies"] = self._flatten_to_list_of_strings(proj["technologies"])

        # Standardize skills
        if "skills" in result:
            result["skills"] = self._flatten_to_list_of_strings(result["skills"])
                
        # Fill in missing list fields with empty lists
        for field in ["skills", "experience", "education", "projects", "certifications"]:
            if field not in result or result[field] is None:
                result[field] = []
                
        # Ensure mandatory string fields are present
        if "name" not in result or not result["name"]:
            result["name"] = "Candidate"
            
        return result

    def _sanitize_jd_dict(self, result: dict) -> dict:
        if not isinstance(result, dict):
            return {}
            
        # Standardize required_skills / preferred_skills / responsibilities / requirements / technologies
        for field in ["required_skills", "preferred_skills", "responsibilities", "requirements", "technologies"]:
            if field in result:
                result[field] = self._flatten_to_list_of_strings(result[field])
            else:
                result[field] = []
                
        if "job_title" not in result or not result["job_title"]:
            result["job_title"] = "Software Engineer"
            
        return result


# Singleton instance
extraction_chains = ExtractionChains()
