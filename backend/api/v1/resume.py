from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from backend.models.schemas import UploadResponse, ErrorResponse, ExtractionResponse, StructuredResume
from backend.services.resume_parser import resume_parser_service
from backend.services.extraction_service import extraction_service
from backend.core.logging import logger

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post("/upload", response_model=UploadResponse, responses={400: {"model": ErrorResponse}})
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse a single resume file.
    Supports PDF, DOCX, and TXT formats.
    """
    try:
        logger.info(f"Received resume upload request for file: {file.filename}")
        parsed_doc, document_id = await resume_parser_service.parse_resume(file)
        return UploadResponse(
            document_id=document_id,
            parsed_document=parsed_doc
        )
    except Exception as e:
        logger.error(f"Error uploading resume: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upload-multiple", response_model=List[UploadResponse], responses={400: {"model": ErrorResponse}})
async def upload_multiple_resumes(files: List[UploadFile] = File(...)):
    """
    Upload and parse multiple resume files.
    Supports PDF, DOCX, and TXT formats.
    """
    try:
        logger.info(f"Received multiple resume upload request for {len(files)} files")
        results = await resume_parser_service.parse_multiple_resumes(files)
        
        responses = [
            UploadResponse(
                document_id=doc_id,
                parsed_document=parsed_doc
            ) for parsed_doc, doc_id in results
        ]
        return responses
    except Exception as e:
        logger.error(f"Error uploading multiple resumes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/extract/{document_id}", response_model=ExtractionResponse, responses={400: {"model": ErrorResponse}})
async def extract_resume_data(document_id: str, raw_text: str = Body(..., embed=True)):
    """
    Extract structured data from a resume using its raw text.
    Returns structured JSON with name, email, phone, skills, experience, education, projects, certifications.
    """
    try:
        logger.info(f"Received extraction request for resume {document_id}")
        structured_data = await extraction_service.extract_resume_data(document_id, raw_text)
        return ExtractionResponse(
            document_id=document_id,
            structured_data=structured_data
        )
    except Exception as e:
        logger.error(f"Error extracting resume data for {document_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
