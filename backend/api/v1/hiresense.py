import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from backend.core.logging import logger
from backend.core.config import settings
from backend.models.schemas import (
    ErrorResponse,
    UploadResponse,
    RankingResponse,
    InterviewQuestionResponse
)
from backend.services.hiresense_orchestration import hiresense_orchestration

router = APIRouter(prefix="/hiresense", tags=["hiresense"])

# Temporary directory for file uploads
UPLOAD_DIR = Path("data") / "temp"
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)


def get_file_type(filename: str) -> str:
    """Get file type from filename extension."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return "pdf"
    elif ext == ".docx":
        return "docx"
    elif ext == ".txt":
        return "txt"
    else:
        raise ValueError(f"Unsupported file type: {ext}")


@router.post("/upload-jd", response_model=dict, responses={400: {"model": ErrorResponse}})
async def upload_job_description(file: UploadFile = File(...)):
    """
    Upload and parse a job description.
    Returns the JD ID.
    """
    try:
        logger.info(f"Uploading job description file: {file.filename}")
        
        # Save uploaded file temporarily
        file_type = get_file_type(file.filename)
        file_path = UPLOAD_DIR / f"{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process using orchestration service
        jd_id = await hiresense_orchestration.upload_and_parse_job_description(file_path, file_type)
        
        # Cleanup temp file
        file_path.unlink()
        
        logger.info(f"Successfully uploaded JD with ID: {jd_id}")
        return {"jd_id": jd_id, "message": "Job description uploaded and parsed successfully"}
    
    except Exception as e:
        logger.error(f"Error uploading JD: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upload-resume", response_model=dict, responses={400: {"model": ErrorResponse}})
async def upload_resume(
    file: UploadFile = File(...),
    jd_id: Optional[str] = Query(None, description="Optional job description ID to associate with")
):
    """
    Upload and parse a single resume.
    Can optionally associate with a job description.
    """
    try:
        logger.info(f"Uploading resume file: {file.filename}")
        
        # Save uploaded file temporarily
        file_type = get_file_type(file.filename)
        file_path = UPLOAD_DIR / f"{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process using orchestration service
        resume_id = await hiresense_orchestration.upload_and_parse_resume(file_path, file_type, jd_id)
        
        # Cleanup temp file
        file_path.unlink()
        
        logger.info(f"Successfully uploaded resume with ID: {resume_id}")
        return {"resume_id": resume_id, "message": "Resume uploaded and parsed successfully"}
    
    except Exception as e:
        logger.error(f"Error uploading resume: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upload-resumes", response_model=dict, responses={400: {"model": ErrorResponse}})
async def upload_multiple_resumes(
    files: List[UploadFile] = File(...),
    jd_id: Optional[str] = Query(None, description="Optional job description ID to associate with")
):
    """
    Upload and parse multiple resumes.
    Can optionally associate with a job description.
    """
    try:
        logger.info(f"Uploading {len(files)} resume files")
        
        uploaded_ids = []
        
        for file in files:
            # Save uploaded file temporarily
            file_type = get_file_type(file.filename)
            file_path = UPLOAD_DIR / f"{file.filename}"
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Process using orchestration service
            resume_id = await hiresense_orchestration.upload_and_parse_resume(file_path, file_type, jd_id)
            uploaded_ids.append(resume_id)
            
            # Cleanup temp file
            file_path.unlink()
        
        logger.info(f"Successfully uploaded {len(uploaded_ids)} resumes")
        return {
            "resume_ids": uploaded_ids,
            "total_uploaded": len(uploaded_ids),
            "message": "Resumes uploaded and parsed successfully"
        }
    
    except Exception as e:
        logger.error(f"Error uploading multiple resumes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rank/{jd_id}", response_model=RankingResponse, responses={400: {"model": ErrorResponse}})
async def rank_candidates(
    jd_id: str,
    ats_weight: float = Query(0.6, description="Weight for ATS score (0-1)"),
    similarity_weight: float = Query(0.4, description="Weight for similarity score (0-1)")
):
    """
    Rank all candidates for a specific job description.
    Returns the ranked list with scores and top candidate.
    """
    try:
        logger.info(f"Ranking candidates for JD ID: {jd_id}")
        
        # Validate weights
        total_weight = ats_weight + similarity_weight
        if total_weight == 0:
            raise ValueError("Total weight cannot be zero")
        
        # Normalize weights
        normalized_ats = ats_weight / total_weight
        normalized_sim = similarity_weight / total_weight
        
        # Rank candidates
        ranking_response = hiresense_orchestration.rank_candidates_for_jd(
            jd_id=jd_id,
            ats_weight=normalized_ats,
            similarity_weight=normalized_sim
        )
        
        return ranking_response
    
    except Exception as e:
        logger.error(f"Error ranking candidates: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/summary/{jd_id}", response_model=dict, responses={400: {"model": ErrorResponse}})
async def get_jd_summary(jd_id: str):
    """
    Get a summary of a job description and its candidates.
    """
    try:
        logger.info(f"Getting summary for JD ID: {jd_id}")
        
        summary = hiresense_orchestration.get_jd_summary(jd_id)
        return summary
    
    except Exception as e:
        logger.error(f"Error getting JD summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/candidate/{resume_id}", response_model=dict, responses={400: {"model": ErrorResponse}})
async def get_candidate_details(
    resume_id: str,
    jd_id: Optional[str] = Query(None, description="Optional job description ID for ranking info")
):
    """
    Get detailed information about a candidate.
    If JD ID is provided, includes interview questions too.
    """
    try:
        logger.info(f"Getting details for candidate: {resume_id}")
        
        details = hiresense_orchestration.get_candidate_details(resume_id, jd_id)
        return details
    
    except Exception as e:
        logger.error(f"Error getting candidate details: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/download-csv/{jd_id}", responses={400: {"model": ErrorResponse}})
async def download_candidates_csv(
    jd_id: str,
    ats_weight: float = Query(0.6, description="Weight for ATS score (0-1)"),
    similarity_weight: float = Query(0.4, description="Weight for similarity score (0-1)")
):
    """
    Download ranked candidates as CSV file.
    """
    try:
        logger.info(f"Downloading CSV for JD ID: {jd_id}")
        
        # First rank candidates
        ranking_response = hiresense_orchestration.rank_candidates_for_jd(
            jd_id=jd_id,
            ats_weight=ats_weight,
            similarity_weight=similarity_weight
        )
        
        # Then export to CSV
        csv_response = hiresense_orchestration.candidate_ranking.export_to_csv(ranking_response)
        return csv_response
    
    except Exception as e:
        logger.error(f"Error downloading CSV: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/download-json/{jd_id}", responses={400: {"model": ErrorResponse}})
async def download_candidates_json(
    jd_id: str,
    ats_weight: float = Query(0.6, description="Weight for ATS score (0-1)"),
    similarity_weight: float = Query(0.4, description="Weight for similarity score (0-1)")
):
    """
    Download ranked candidates as JSON file.
    """
    try:
        logger.info(f"Downloading JSON for JD ID: {jd_id}")
        
        # First rank candidates
        ranking_response = hiresense_orchestration.rank_candidates_for_jd(
            jd_id=jd_id,
            ats_weight=ats_weight,
            similarity_weight=similarity_weight
        )
        
        # Then export to JSON
        json_response = hiresense_orchestration.candidate_ranking.export_to_json(ranking_response)
        return json_response
    
    except Exception as e:
        logger.error(f"Error downloading JSON: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
