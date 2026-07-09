from fastapi import APIRouter, HTTPException
from backend.models.schemas import ATSRequest, ATSResult, ErrorResponse
from backend.services.ats_scoring import ats_scoring_service
from backend.core.logging import logger

router = APIRouter(prefix="/ats", tags=["ats"])


@router.post("/score", response_model=ATSResult, responses={400: {"model": ErrorResponse}})
async def calculate_ats_score(request: ATSRequest):
    """
    Calculate ATS score for a resume against a job description.
    Returns total score, score breakdown, reasoning, strengths, weaknesses, and missing skills.
    """
    try:
        logger.info("Received ATS score calculation request")
        result = ats_scoring_service.calculate_ats_score(
            resume_structured=request.resume_structured,
            jd_structured=request.jd_structured
        )
        return result
    except Exception as e:
        logger.error(f"Error calculating ATS score: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
