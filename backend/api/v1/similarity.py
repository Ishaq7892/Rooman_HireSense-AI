from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from backend.models.schemas import ErrorResponse, StructuredResume, StructuredJobDescription
from backend.services.similarity_engine import similarity_engine
from backend.core.logging import logger

router = APIRouter(prefix="/similarity", tags=["similarity"])


# Request models
class CalculateSimilarityRequest(BaseModel):
    resume_raw_text: str = Field(..., description="Raw text from the resume")
    jd_raw_text: str = Field(..., description="Raw text from the job description")
    resume_structured: Optional[StructuredResume] = Field(None, description="Structured data from the resume (optional)")
    jd_structured: Optional[StructuredJobDescription] = Field(None, description="Structured data from the job description (optional)")


class RankResumesRequest(BaseModel):
    jd_raw_text: str = Field(..., description="Raw text from the job description")
    resumes: List[Dict] = Field(..., description="List of resume dictionaries, each with 'raw_text' and optional 'structured_data' and 'metadata'")
    jd_structured: Optional[StructuredJobDescription] = Field(None, description="Structured data from the job description (optional)")


class SimilarityBreakdownRequest(BaseModel):
    resume_raw_text: str = Field(..., description="Raw text from the resume")
    jd_raw_text: str = Field(..., description="Raw text from the job description")
    resume_structured: Optional[StructuredResume] = Field(None, description="Structured data from the resume (optional)")
    jd_structured: Optional[StructuredJobDescription] = Field(None, description="Structured data from the job description (optional)")


# Response models
class CalculateSimilarityResponse(BaseModel):
    similarity_score: float = Field(..., description="Cosine similarity score between 0 and 1")


class RankedResumeItem(BaseModel):
    resume_data: Dict = Field(..., description="Resume data including raw text, structured data, and metadata")
    similarity_score: float = Field(..., description="Cosine similarity score between 0 and 1")


class RankResumesResponse(BaseModel):
    ranked_resumes: List[RankedResumeItem] = Field(..., description="List of resumes sorted by similarity (highest first)")


class SimilarityBreakdownResponse(BaseModel):
    overall_similarity: float = Field(..., description="Overall cosine similarity score")
    score_category: str = Field(..., description="Category (excellent, good, fair, poor)")
    explanation: str = Field(..., description="Explanation of the similarity score")
    score_range: Dict[str, tuple] = Field(..., description="Score ranges for each category")


@router.post("/calculate", response_model=CalculateSimilarityResponse, responses={400: {"model": ErrorResponse}})
async def calculate_similarity(request: CalculateSimilarityRequest):
    """
    Calculate cosine similarity between a resume and a job description.
    Returns a score between 0 (no similarity) and 1 (identical).
    """
    try:
        logger.info("Received similarity calculation request")
        score = similarity_engine.calculate_resume_jd_similarity(
            resume_raw_text=request.resume_raw_text,
            jd_raw_text=request.jd_raw_text,
            resume_structured=request.resume_structured,
            jd_structured=request.jd_structured
        )
        return CalculateSimilarityResponse(similarity_score=score)
    except Exception as e:
        logger.error(f"Error calculating similarity: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rank", response_model=RankResumesResponse, responses={400: {"model": ErrorResponse}})
async def rank_resumes(request: RankResumesRequest):
    """
    Rank a list of resumes by their cosine similarity to a job description.
    Returns resumes sorted from most similar to least similar.
    """
    try:
        logger.info("Received resume ranking request")
        ranked = similarity_engine.rank_resumes_for_jd(
            jd_raw_text=request.jd_raw_text,
            resumes=request.resumes,
            jd_structured=request.jd_structured
        )
        formatted_ranked = [
            RankedResumeItem(resume_data=resume_data, similarity_score=score)
            for resume_data, score in ranked
        ]
        return RankResumesResponse(ranked_resumes=formatted_ranked)
    except Exception as e:
        logger.error(f"Error ranking resumes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/breakdown", response_model=SimilarityBreakdownResponse, responses={400: {"model": ErrorResponse}})
async def get_similarity_breakdown(request: SimilarityBreakdownRequest):
    """
    Get a detailed breakdown of the similarity score, including category and explanation.
    """
    try:
        logger.info("Received similarity breakdown request")
        breakdown = similarity_engine.get_similarity_breakdown(
            resume_raw_text=request.resume_raw_text,
            jd_raw_text=request.jd_raw_text,
            resume_structured=request.resume_structured,
            jd_structured=request.jd_structured
        )
        return SimilarityBreakdownResponse(**breakdown)
    except Exception as e:
        logger.error(f"Error getting similarity breakdown: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
