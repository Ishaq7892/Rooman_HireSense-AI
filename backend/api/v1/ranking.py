from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.models.schemas import RankingRequest, RankingResponse, ErrorResponse
from backend.services.candidate_ranking import candidate_ranking_service
from backend.core.logging import logger

router = APIRouter(prefix="/ranking", tags=["ranking"])


@router.post("/rank", response_model=RankingResponse, responses={400: {"model": ErrorResponse}})
async def rank_candidates(request: RankingRequest):
    """
    Rank candidates based on ATS and similarity scores.
    Returns ranked list, top candidate, and score weights.
    """
    try:
        logger.info("Received candidate ranking request")
        result = candidate_ranking_service.rank_candidates(
            job_description_data=request.job_description_data,
            job_description_raw_text=request.job_description_raw_text,
            candidates=request.candidates,
            ats_weight=request.ats_weight,
            similarity_weight=request.similarity_weight
        )
        return result
    except Exception as e:
        logger.error(f"Error ranking candidates: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/export/csv", responses={400: {"model": ErrorResponse}})
async def export_rankings_to_csv(request: RankingRequest) -> StreamingResponse:
    """
    Rank candidates and export results to CSV format.
    """
    try:
        logger.info("Received CSV export request")
        ranking_result = candidate_ranking_service.rank_candidates(
            job_description_data=request.job_description_data,
            job_description_raw_text=request.job_description_raw_text,
            candidates=request.candidates,
            ats_weight=request.ats_weight,
            similarity_weight=request.similarity_weight
        )
        return candidate_ranking_service.export_to_csv(ranking_result)
    except Exception as e:
        logger.error(f"Error exporting to CSV: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/export/json", responses={400: {"model": ErrorResponse}})
async def export_rankings_to_json(request: RankingRequest) -> StreamingResponse:
    """
    Rank candidates and export results to JSON format.
    """
    try:
        logger.info("Received JSON export request")
        ranking_result = candidate_ranking_service.rank_candidates(
            job_description_data=request.job_description_data,
            job_description_raw_text=request.job_description_raw_text,
            candidates=request.candidates,
            ats_weight=request.ats_weight,
            similarity_weight=request.similarity_weight
        )
        return candidate_ranking_service.export_to_json(ranking_result)
    except Exception as e:
        logger.error(f"Error exporting to JSON: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
