from typing import List, Dict
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from backend.models.schemas import ErrorResponse, StructuredResume, StructuredJobDescription
from backend.services.embedding_service import embedding_service
from backend.core.logging import logger

router = APIRouter(prefix="/embeddings", tags=["embeddings"])


# Request models
class EmbedResumeRequest(BaseModel):
    document_id: str = Field(..., description="Unique identifier for the resume")
    raw_text: str = Field(..., description="Raw text from the resume")
    structured_data: StructuredResume = Field(None, description="Structured data extracted from the resume (optional)")


class EmbedJobDescriptionRequest(BaseModel):
    document_id: str = Field(..., description="Unique identifier for the job description")
    raw_text: str = Field(..., description="Raw text from the job description")
    structured_data: StructuredJobDescription = Field(None, description="Structured data extracted from the job description (optional)")


class SearchSimilarResumesRequest(BaseModel):
    jd_document_id: str = Field(..., description="Unique identifier for the job description")
    raw_text: str = Field(..., description="Raw text from the job description")
    k: int = Field(10, description="Number of top results to return (default: 10)")


# Response models
class SimilarResumeResult(BaseModel):
    metadata: Dict = Field(..., description="Metadata of the similar resume")
    distance: float = Field(..., description="Distance score (lower = more similar)")


class SearchSimilarResumesResponse(BaseModel):
    results: List[SimilarResumeResult] = Field(..., description="List of similar resumes with scores")


@router.post("/resume", responses={400: {"model": ErrorResponse}})
async def embed_resume(request: EmbedResumeRequest):
    """
    Generate embedding for a resume and add it to the FAISS vector store.
    Uses Sentence Transformers all-MiniLM-L6-v2.
    """
    try:
        logger.info(f"Received embedding request for resume {request.document_id}")
        embedding_service.embed_resume(
            document_id=request.document_id,
            raw_text=request.raw_text,
            structured_data=request.structured_data
        )
        return {"message": "Resume embedded successfully", "document_id": request.document_id}
    except Exception as e:
        logger.error(f"Error embedding resume: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/job-description", responses={400: {"model": ErrorResponse}})
async def embed_job_description(request: EmbedJobDescriptionRequest):
    """
    Generate embedding for a job description and add it to the FAISS vector store.
    Uses Sentence Transformers all-MiniLM-L6-v2.
    """
    try:
        logger.info(f"Received embedding request for job description {request.document_id}")
        embedding_service.embed_job_description(
            document_id=request.document_id,
            raw_text=request.raw_text,
            structured_data=request.structured_data
        )
        return {"message": "Job description embedded successfully", "document_id": request.document_id}
    except Exception as e:
        logger.error(f"Error embedding job description: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/search-similar-resumes", response_model=SearchSimilarResumesResponse, responses={400: {"model": ErrorResponse}})
async def search_similar_resumes(request: SearchSimilarResumesRequest):
    """
    Search for resumes similar to a job description using FAISS.
    Returns top k results with similarity scores.
    """
    try:
        logger.info(f"Received search request for JD {request.jd_document_id}")
        results = embedding_service.search_similar_resumes(
            jd_document_id=request.jd_document_id,
            raw_text=request.raw_text,
            k=request.k
        )
        formatted_results = [
            SimilarResumeResult(metadata=md, distance=d)
            for md, d in results
        ]
        return SearchSimilarResumesResponse(results=formatted_results)
    except Exception as e:
        logger.error(f"Error searching similar resumes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/resume-store", responses={400: {"model": ErrorResponse}})
async def clear_resume_store():
    """Clear all resumes from the FAISS vector store."""
    try:
        embedding_service.clear_resume_store()
        return {"message": "Resume vector store cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing resume store: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/job-description-store", responses={400: {"model": ErrorResponse}})
async def clear_jd_store():
    """Clear all job descriptions from the FAISS vector store."""
    try:
        embedding_service.clear_jd_store()
        return {"message": "Job description vector store cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing JD store: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
