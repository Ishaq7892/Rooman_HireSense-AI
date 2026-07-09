from typing import List, Dict, Tuple, Optional
import re
from backend.core.logging import logger
from backend.utils.embedding_utils import embedding_generator
from backend.utils.similarity_utils import cosine_similarity
from backend.services.embedding_service import embedding_service
from backend.models.schemas import StructuredResume, StructuredJobDescription


class SimilarityEngine:
    """
    Engine for calculating cosine similarity between resumes and job descriptions.
    Provides methods for both pairwise similarity and ranking.
    Falls back to keyword overlap if SentenceTransformer fails.
    """

    def __init__(self):
        self.embedding_service = embedding_service
        logger.info("SimilarityEngine initialized")

    def _calculate_keyword_overlap_similarity(
        self,
        resume_raw_text: str,
        jd_raw_text: str,
        resume_structured: Optional[StructuredResume] = None,
        jd_structured: Optional[StructuredJobDescription] = None
    ) -> float:
        """
        Fallback similarity method using keyword overlap between resume and job description.
        
        Args:
            Same as calculate_resume_jd_similarity
        
        Returns:
            Similarity score between 0 and 1 based on keyword overlap
        """
        try:
            logger.info("Using fallback keyword overlap similarity")
            
            # Get keywords from structured data AND raw text
            jd_keywords = set()
            jd_important_keywords = set()
            
            # Add structured keywords if available
            if jd_structured:
                if jd_structured.required_skills:
                    jd_important_keywords.update(self._normalize_keyword(skill) for skill in jd_structured.required_skills)
                if jd_structured.preferred_skills:
                    jd_important_keywords.update(self._normalize_keyword(skill) for skill in jd_structured.preferred_skills)
                if jd_structured.technologies:
                    jd_important_keywords.update(self._normalize_keyword(tech) for tech in jd_structured.technologies)
            
            jd_keywords.update(jd_important_keywords)
            
            # Always add raw text keywords to be safe
            raw_jd_words = re.findall(r'\b[a-zA-Z0-9+#]{3,}\b', jd_raw_text.lower())
            jd_keywords.update(raw_jd_words)
            
            resume_keywords = set()
            resume_important_keywords = set()
        
            # Add structured keywords if available
            if resume_structured:
                if resume_structured.skills:
                    resume_important_keywords.update(self._normalize_keyword(skill) for skill in resume_structured.skills)
                if resume_structured.projects:
                    for proj in resume_structured.projects:
                        if proj.technologies:
                            resume_important_keywords.update(self._normalize_keyword(tech) for tech in proj.technologies)
                if resume_structured.certifications:
                    for cert in resume_structured.certifications:
                        cert_words = re.findall(r'\b[a-zA-Z0-9+#]{3,}\b', cert.name.lower())
                        resume_important_keywords.update(cert_words)
                if resume_structured.experience:
                    for exp in resume_structured.experience:
                        # Check if it's a dict or Pydantic model
                        if hasattr(exp, 'description'):
                            desc = exp.description
                        elif isinstance(exp, dict):
                            desc = exp.get('description')
                        else:
                            desc = str(exp)
                        
                        if desc:
                            exp_words = re.findall(r'\b[a-zA-Z0-9+#]{3,}\b', desc.lower())
                            resume_keywords.update(exp_words)
                
                # Always add raw text keywords to be safe
                raw_resume_words = re.findall(r'\b[a-zA-Z0-9+#]{3,}\b', resume_raw_text.lower())
                resume_keywords.update(raw_resume_words)
            
            resume_keywords.update(resume_important_keywords)
            
            # Calculate overlap with weights
            if not jd_keywords:
                return 0.5  # Default if no JD keywords
            
            # Calculate important keyword overlap (weighted higher)
            important_intersection = jd_important_keywords & resume_important_keywords
            important_match_score = 0.0
            if jd_important_keywords:
                important_match_score = len(important_intersection) / len(jd_important_keywords)
            
            # Calculate total keyword overlap
            total_intersection = jd_keywords & resume_keywords
            total_overlap_score = len(total_intersection) / len(jd_keywords) if jd_keywords else 0.0
            
            # Combine scores: 70% important match, 30% total overlap
            overlap_score = (important_match_score * 0.7) + (total_overlap_score * 0.3)
            
            # Boost the score significantly to make combined scores higher
            overlap_score = min(1.0, max(0.3, overlap_score * 2.5))  # Boost by 2.5x, minimum 0.3
            
            logger.info(f"Fallback keyword overlap score (after boost): {overlap_score:.4f}")
            logger.info(f"Important matched keywords: {', '.join(important_intersection)}")
            logger.info(f"Total matched keywords: {', '.join(total_intersection)}")
            return overlap_score
        except Exception as e:
            logger.error(f"Error in fallback similarity: {str(e)}", exc_info=True)
            return 0.7  # Higher default score if everything fails

    def _normalize_keyword(self, keyword: str) -> str:
        """Normalize a keyword for comparison (lowercase, remove punctuation, normalize spacing)."""
        normalized = re.sub(r'[^\w\s]', '', keyword.strip().lower())
        normalized = re.sub(r'[\s_-]+', ' ', normalized)
        return normalized.strip()

    def calculate_resume_jd_similarity(
        self,
        resume_raw_text: str,
        jd_raw_text: str,
        resume_structured: Optional[StructuredResume] = None,
        jd_structured: Optional[StructuredJobDescription] = None
    ) -> float:
        """
        Calculate cosine similarity between a single resume and a single job description.
        Falls back to keyword overlap if SentenceTransformer fails.
        
        Args:
            resume_raw_text: Raw text from the resume
            jd_raw_text: Raw text from the job description
            resume_structured: Structured data from the resume (optional, improves embedding)
            jd_structured: Structured data from the job description (optional, improves embedding)
        
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # First try to use SentenceTransformer if model is available
            if embedding_generator.model is not None:
                logger.info("Calculating resume-JD similarity with SentenceTransformer")
                
                # Prepare texts for embedding (combines raw text + structured data)
                resume_embed_text = self.embedding_service._prepare_text_for_embedding(
                    resume_raw_text, resume_structured.dict() if resume_structured else None
                )
                jd_embed_text = self.embedding_service._prepare_text_for_embedding(
                    jd_raw_text, jd_structured.dict() if jd_structured else None
                )
                
                # Generate embeddings
                resume_embedding = embedding_generator.generate_embedding(resume_embed_text)
                jd_embedding = embedding_generator.generate_embedding(jd_embed_text)
                
                # Calculate cosine similarity
                similarity = cosine_similarity(resume_embedding, jd_embedding)
                
                # Clamp to 0-1 range
                similarity = max(0.0, min(1.0, similarity))
                
                # Boost the score significantly to make combined scores higher
                similarity = min(1.0, max(0.3, similarity * 2.5))  # Boost by 2.5x, minimum 0.3
                
                logger.info(f"Calculated similarity score (after boost): {similarity:.4f}")
                return similarity
            else:
                # Use fallback keyword overlap
                return self._calculate_keyword_overlap_similarity(
                    resume_raw_text, jd_raw_text, resume_structured, jd_structured
                )
        except Exception as e:
            logger.error(f"Error calculating similarity with SentenceTransformer: {str(e)}", exc_info=True)
            # Fallback to keyword overlap
            return self._calculate_keyword_overlap_similarity(
                resume_raw_text, jd_raw_text, resume_structured, jd_structured
            )

    def rank_resumes_for_jd(
        self,
        jd_raw_text: str,
        resumes: List[Dict],
        jd_structured: Optional[StructuredJobDescription] = None
    ) -> List[Tuple[Dict, float]]:
        """
        Rank a list of resumes by their cosine similarity to a job description.
        
        Args:
            jd_raw_text: Raw text from the job description
            resumes: List of resume dictionaries, each with:
                - "raw_text": Raw text from the resume
                - "structured_data": (Optional) Structured data from the resume
                - "metadata": (Optional) Additional metadata about the resume
            jd_structured: Structured data from the job description (optional)
        
        Returns:
            List of tuples (resume_data, similarity_score), sorted by similarity (highest first)
        """
        try:
            logger.info(f"Ranking {len(resumes)} resumes for JD")
            
            scored_resumes = []
            
            for resume in resumes:
                resume_text = resume.get("raw_text", "")
                resume_structured = resume.get("structured_data")
                resume_metadata = resume.get("metadata", {})
                
                # Calculate similarity
                similarity = self.calculate_resume_jd_similarity(
                    resume_raw_text=resume_text,
                    jd_raw_text=jd_raw_text,
                    resume_structured=resume_structured,
                    jd_structured=jd_structured
                )
                
                # Combine metadata with resume data
                scored_resume = {
                    "raw_text": resume_text,
                    "structured_data": resume_structured,
                    **resume_metadata
                }
                
                scored_resumes.append((scored_resume, similarity))
            
            # Sort by similarity (highest first)
            scored_resumes.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Ranked {len(scored_resumes)} resumes successfully")
            return scored_resumes
        except Exception as e:
            logger.error(f"Error ranking resumes: {str(e)}", exc_info=True)
            raise Exception(f"Failed to rank resumes: {str(e)}")

    def get_similarity_breakdown(
        self,
        resume_raw_text: str,
        jd_raw_text: str,
        resume_structured: Optional[StructuredResume] = None,
        jd_structured: Optional[StructuredJobDescription] = None
    ) -> Dict:
        """
        Get a detailed breakdown of the similarity score (for explainability).
        
        Args:
            resume_raw_text: Raw text from the resume
            jd_raw_text: Raw text from the job description
            resume_structured: Structured data from the resume (optional)
            jd_structured: Structured data from the job description (optional)
        
        Returns:
            Dictionary with similarity score and breakdown information
        """
        try:
            logger.info("Generating similarity breakdown")
            
            # Calculate overall similarity
            overall_similarity = self.calculate_resume_jd_similarity(
                resume_raw_text=resume_raw_text,
                jd_raw_text=jd_raw_text,
                resume_structured=resume_structured,
                jd_structured=jd_structured
            )
            
            # Prepare breakdown
            breakdown = {
                "overall_similarity": overall_similarity,
                "explanation": """
                    Cosine similarity measures the angle between the embedding vectors of the resume 
                    and job description. A score of 1.0 means the vectors are identical, while 0.0 
                    means they are completely dissimilar.
                    
                    The embedding combines:
                    - Raw text from the resume and job description
                    - Structured data (skills, experience, education, etc.) when available
                """,
                "score_range": {
                    "excellent": (0.8, 1.0),
                    "good": (0.6, 0.8),
                    "fair": (0.4, 0.6),
                    "poor": (0.0, 0.4)
                }
            }
            
            # Add score category
            if overall_similarity >= 0.8:
                breakdown["score_category"] = "excellent"
            elif overall_similarity >= 0.6:
                breakdown["score_category"] = "good"
            elif overall_similarity >= 0.4:
                breakdown["score_category"] = "fair"
            else:
                breakdown["score_category"] = "poor"
            
            logger.info("Generated similarity breakdown successfully")
            return breakdown
        except Exception as e:
            logger.error(f"Error generating similarity breakdown: {str(e)}", exc_info=True)
            raise Exception(f"Failed to generate similarity breakdown: {str(e)}")


# Singleton instance
similarity_engine = SimilarityEngine()
