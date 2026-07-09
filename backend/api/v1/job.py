from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from backend.models.schemas import UploadResponse, ErrorResponse, ExtractionResponse, StructuredJobDescription
from backend.services.resume_parser import resume_parser_service
from backend.services.extraction_service import extraction_service
from backend.core.logging import logger

router = APIRouter(prefix="/job", tags=["job"])


@router.post("/upload", response_model=UploadResponse, responses={400: {"model": ErrorResponse}})
async def upload_job_description(file: UploadFile = File(...)):
    """
    Upload and parse a job description file.
    Supports PDF, DOCX, and TXT formats.
    """
    try:
        logger.info(f"Received job description upload request for file: {file.filename}")
        parsed_doc, document_id = await resume_parser_service.parse_job_description(file)
        return UploadResponse(
            document_id=document_id,
            parsed_document=parsed_doc
        )
    except Exception as e:
        logger.error(f"Error uploading job description: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/extract/{document_id}", response_model=ExtractionResponse, responses={400: {"model": ErrorResponse}})
async def extract_job_description_data(document_id: str, raw_text: str = Body(..., embed=True)):
    """
    Extract structured data from a job description using its raw text.
    Returns structured JSON with job title, skills, responsibilities, requirements, etc.
    """
    try:
        logger.info(f"Received extraction request for job description {document_id}")
        structured_data = await extraction_service.extract_job_description_data(document_id, raw_text)
        return ExtractionResponse(
            document_id=document_id,
            structured_data=structured_data
        )
    except Exception as e:
        logger.error(f"Error extracting job description data for {document_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
