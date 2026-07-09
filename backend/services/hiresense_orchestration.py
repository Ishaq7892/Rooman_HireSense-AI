import uuid
from pathlib import Path
from typing import List, Optional
from backend.core.logging import logger
from backend.models.schemas import (
    ParsedDocument,
    StructuredResume,
    StructuredJobDescription,
    CandidateData,
    RankingResponse,
    InterviewQuestionResponse,
    InterviewQuestionRequest
)
from backend.services.resume_parser import resume_parser_service
from backend.services.extraction_service import extraction_service
from backend.services.embedding_service import embedding_service
from backend.services.candidate_ranking import candidate_ranking_service
from backend.services.interview_question_generator import interview_question_generator
from backend.core.config import settings
from backend.utils.parser import parse_document


class HireSenseOrchestration:
    """
    Orchestration service that ties together all HireSense AI services.
    Handles complete resume screening workflows.
    """

    def __init__(self):
        self.resume_parser = resume_parser_service
        self.extraction_service = extraction_service
        self.embedding_service = embedding_service
        self.candidate_ranking = candidate_ranking_service
        self.interview_generator = interview_question_generator
        
        # In-memory storage for simplicity (in real app, use a DB)
        self.jd_store = {}  # jd_id -> (raw_text, structured_data)
        self.resume_store = {}  # resume_id -> (raw_text, structured_data)
        self.candidates = {}  # jd_id -> List[CandidateData]
        self.ranking_results = {}  # jd_id -> RankingResponse
        
        logger.info("HireSenseOrchestration initialized")

    async def upload_and_parse_job_description(self, file_path: Path, file_type: str) -> str:
        """
        Upload and parse a job description.

        Args:
            file_path: Path to uploaded file
            file_type: Type of file (pdf/docx/txt)

        Returns:
            Job description ID
        """
        try:
            logger.info("Uploading and parsing job description")
            
            # Generate unique ID
            jd_id = str(uuid.uuid4())
            
            # Parse raw text
            raw_text = parse_document(str(file_path), file_path.name)
            
            # Extract structured data
            structured_data = await self.extraction_service.extract_job_description_data(jd_id, raw_text)
            
            # Store in memory
            self.jd_store[jd_id] = (raw_text, structured_data)
            self.candidates[jd_id] = []
            
            logger.info(f"Job description uploaded and parsed with ID: {jd_id}")
            return jd_id
        except Exception as e:
            logger.error(f"Error uploading job description: {str(e)}", exc_info=True)
            raise Exception(f"Failed to upload job description: {str(e)}")

    async def upload_and_parse_resume(self, file_path: Path, file_type: str, jd_id: Optional[str] = None) -> str:
        """
        Upload and parse a single resume.

        Args:
            file_path: Path to uploaded file
            file_type: Type of file (pdf/docx/txt)
            jd_id: Optional ID of job description to associate with

        Returns:
            Resume ID
        """
        try:
            logger.info("Uploading and parsing resume")
            
            # Generate unique ID
            resume_id = str(uuid.uuid4())
            
            # Parse raw text
            raw_text = parse_document(str(file_path), file_path.name)
            
            # Extract structured data
            structured_data = await self.extraction_service.extract_resume_data(resume_id, raw_text)
            
            # Store in memory
            self.resume_store[resume_id] = (raw_text, structured_data)
            
            # Associate with JD if provided
            if jd_id and jd_id in self.candidates:
                candidate = CandidateData(
                    document_id=resume_id,
                    raw_text=raw_text,
                    structured_data=structured_data
                )
                self.candidates[jd_id].append(candidate)
            
            logger.info(f"Resume uploaded and parsed with ID: {resume_id}")
            return resume_id
        except Exception as e:
            logger.error(f"Error uploading resume: {str(e)}", exc_info=True)
            raise Exception(f"Failed to upload resume: {str(e)}")

    def rank_candidates_for_jd(self, jd_id: str, ats_weight: float = 0.6, similarity_weight: float = 0.4) -> RankingResponse:
        """
        Rank all candidates for a specific job description.

        Args:
            jd_id: Job description ID
            ats_weight: Weight for ATS score (0-1)
            similarity_weight: Weight for similarity score (0-1)

        Returns:
            Ranking response with ranked candidates
        """
        try:
            logger.info(f"Ranking candidates for JD ID: {jd_id}")
            
            # Check if JD exists
            if jd_id not in self.jd_store or jd_id not in self.candidates:
                raise ValueError(f"Job description with ID {jd_id} not found")
            
            jd_raw_text, jd_structured = self.jd_store[jd_id]
            candidates = self.candidates[jd_id]
            
            # Generate embeddings
            self.embedding_service.embed_job_description(
                raw_text=jd_raw_text,
                document_id=jd_id,
                structured_data=jd_structured
            )
            
            for candidate in candidates:
                self.embedding_service.embed_resume(
                    raw_text=candidate.raw_text,
                    document_id=candidate.document_id,
                    structured_data=candidate.structured_data
                )
            
            # Rank candidates
            ranking_response = self.candidate_ranking.rank_candidates(
                job_description_data=jd_structured,
                job_description_raw_text=jd_raw_text,
                candidates=candidates,
                ats_weight=ats_weight,
                similarity_weight=similarity_weight
            )
            
            # Store in cache
            self.ranking_results[jd_id] = ranking_response
            
            logger.info(f"Successfully ranked {len(candidates)} candidates")
            return ranking_response
        except Exception as e:
            logger.error(f"Error ranking candidates: {str(e)}", exc_info=True)
            raise Exception(f"Failed to rank candidates: {str(e)}")

    def get_candidate_details(self, resume_id: str, jd_id: Optional[str] = None) -> dict:
        """
        Get detailed information about a candidate.

        Args:
            resume_id: Resume ID
            jd_id: Optional job description ID to include score/rank

        Returns:
            Candidate details
        """
        try:
            logger.info(f"Getting candidate details for resume ID: {resume_id}")
            
            if resume_id not in self.resume_store:
                import json
                file_path = Path(__file__).resolve().parent.parent.parent / "data" / "resumes" / f"{resume_id}_structured.json"
                if file_path.exists():
                    logger.info(f"Loading resume {resume_id} from disk")
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    structured_data = StructuredResume(**data)
                    self.resume_store[resume_id] = ("", structured_data)
                else:
                    raise ValueError(f"Resume with ID {resume_id} not found")
            
            raw_text, structured_data = self.resume_store[resume_id]
            
            candidate_details = {
                "resume_id": resume_id,
                "name": structured_data.name,
                "email": structured_data.email,
                "phone": structured_data.phone,
                "skills": structured_data.skills,
                "experience": structured_data.experience,
                "education": structured_data.education,
                "projects": structured_data.projects,
                "certifications": structured_data.certifications,
                "raw_text": raw_text
            }
            
            # If JD ID is provided, get ranking info too
            if jd_id:
                # Load job description from disk if missing from memory
                if jd_id not in self.jd_store:
                    import json
                    file_path = Path(__file__).resolve().parent.parent.parent / "data" / "job_descriptions" / f"{jd_id}_structured.json"
                    if file_path.exists():
                        logger.info(f"Loading job description {jd_id} from disk")
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        jd_structured = StructuredJobDescription(**data)
                        self.jd_store[jd_id] = ("", jd_structured)
                        self.candidates[jd_id] = []
                
                if jd_id in self.jd_store:
                    # Find candidate in candidates list and associate if not already present
                    if jd_id not in self.candidates:
                        self.candidates[jd_id] = []
                    
                    candidate_found = None
                    for candidate in self.candidates[jd_id]:
                        if candidate.document_id == resume_id:
                            candidate_found = candidate
                            break
                    
                    if not candidate_found:
                        candidate_found = CandidateData(
                            document_id=resume_id,
                            raw_text=raw_text,
                            structured_data=structured_data
                        )
                        self.candidates[jd_id].append(candidate_found)

                    # Check if we have cached ranking results
                    strengths = []
                    weaknesses = []
                    ats_score = 0.0
                    similarity_score = 0.0
                    combined_score = 0.0
                    reasoning = ""
                    
                    ranking_found = False
                    if jd_id in self.ranking_results:
                        for r_cand in self.ranking_results[jd_id].ranked_candidates:
                            if r_cand.document_id == resume_id:
                                strengths = r_cand.strengths
                                weaknesses = r_cand.weaknesses
                                ats_score = r_cand.ats_score
                                similarity_score = r_cand.similarity_score
                                combined_score = r_cand.combined_score
                                reasoning = r_cand.reasoning
                                ranking_found = True
                                break
                    
                    # If not found in cache, calculate ATS score on the fly (but don't cache)
                    if not ranking_found:
                        jd_raw, jd_structured = self.jd_store[jd_id]
                        ats_result = self.candidate_ranking.ats_scoring_service.calculate_ats_score(
                            resume_structured=structured_data,
                            jd_structured=jd_structured
                        )
                        strengths = ats_result.strengths
                        weaknesses = ats_result.weaknesses
                        ats_score = ats_result.total_score
                        reasoning = ats_result.reasoning
                    
                    candidate_details["strengths"] = strengths
                    candidate_details["weaknesses"] = weaknesses
                    candidate_details["ats_score"] = ats_score
                    candidate_details["similarity_score"] = similarity_score
                    candidate_details["combined_score"] = combined_score
                    candidate_details["reasoning"] = reasoning

                    # Generate interview questions for this candidate
                    jd_raw, jd_structured = self.jd_store[jd_id]
                    
                    # Get missing skills
                    missing_skills = []
                    for skill in jd_structured.required_skills:
                        if skill not in structured_data.skills:
                            missing_skills.append(skill)
                    
                    interview_questions = self.interview_generator.generate_questions(
                        InterviewQuestionRequest(
                            candidate_name=structured_data.name,
                            structured_resume=structured_data,
                            structured_job_description=jd_structured,
                            missing_skills=missing_skills
                        )
                    )
                    
                    candidate_details["interview_questions"] = interview_questions
            
            logger.info("Retrieved candidate details successfully")
            return candidate_details
        except Exception as e:
            logger.error(f"Error getting candidate details: {str(e)}", exc_info=True)
            raise Exception(f"Failed to get candidate details: {str(e)}")

    def get_jd_summary(self, jd_id: str) -> dict:
        """
        Get a summary of a job description and its candidates.

        Args:
            jd_id: Job description ID

        Returns:
            Summary information
        """
        try:
            logger.info(f"Getting JD summary for ID: {jd_id}")
            
            if jd_id not in self.jd_store:
                raise ValueError(f"Job description with ID {jd_id} not found")
            
            jd_raw, jd_structured = self.jd_store[jd_id]
            candidates = self.candidates.get(jd_id, [])
            
            summary = {
                "jd_id": jd_id,
                "job_title": jd_structured.job_title,
                "company": jd_structured.company,
                "location": jd_structured.location,
                "required_skills": jd_structured.required_skills,
                "technologies": jd_structured.technologies,
                "total_candidates": len(candidates)
            }
            
            logger.info("Retrieved JD summary successfully")
            return summary
        except Exception as e:
            logger.error(f"Error getting JD summary: {str(e)}", exc_info=True)
            raise Exception(f"Failed to get JD summary: {str(e)}")


# Singleton instance
hiresense_orchestration = HireSenseOrchestration()
