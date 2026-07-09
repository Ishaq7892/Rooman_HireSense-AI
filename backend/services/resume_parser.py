import os
import uuid
from pathlib import Path
from typing import List
from fastapi import UploadFile
from backend.core.config import settings
from backend.core.logging import logger
from backend.models.schemas import ParsedDocument
from backend.utils.parser import parse_document, get_file_type


class ResumeParserService:
    """
    Service class for parsing resumes and job descriptions.
    Handles file upload, storage, and text extraction.
    """

    def __init__(self):
        self.data_dir = Path("data")
        self.resumes_dir = self.data_dir / "resumes"
        self.jd_dir = self.data_dir / "job_descriptions"
        
        # Ensure directories exist
        self.resumes_dir.mkdir(parents=True, exist_ok=True)
        self.jd_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("ResumeParserService initialized")

    async def save_uploaded_file(self, file: UploadFile, target_dir: Path) -> tuple[str, str]:
        """
        Save an uploaded file to the target directory.

        Args:
            file: UploadFile object from FastAPI
            target_dir: Directory to save the file

        Returns:
            Tuple of (file_path, document_id)
        """
        document_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        file_name = f"{document_id}{file_extension}"
        file_path = target_dir / file_name

        logger.info(f"Saving uploaded file to: {file_path}")

        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            logger.info(f"File saved successfully: {file_path}")
            return str(file_path), document_id
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}", exc_info=True)
            raise Exception(f"Failed to save file: {str(e)}")

    async def parse_resume(self, file: UploadFile) -> tuple[ParsedDocument, str]:
        """
        Parse a single resume file.

        Args:
            file: UploadFile object (resume)

        Returns:
            Tuple of (ParsedDocument object, document_id)
        """
        logger.info(f"Parsing resume file: {file.filename}")
        
        # Save the file
        file_path, document_id = await self.save_uploaded_file(file, self.resumes_dir)
        
        # Parse the document
        raw_text = parse_document(file_path, file.filename)
        file_type = get_file_type(file.filename)
        
        parsed_doc = ParsedDocument(
            file_name=file.filename,
            file_type=file_type,
            raw_text=raw_text
        )
        
        logger.info(f"Resume parsed successfully: {document_id}")
        return parsed_doc, document_id

    async def parse_job_description(self, file: UploadFile) -> tuple[ParsedDocument, str]:
        """
        Parse a job description file.

        Args:
            file: UploadFile object (job description)

        Returns:
            Tuple of (ParsedDocument object, document_id)
        """
        logger.info(f"Parsing job description file: {file.filename}")
        
        # Save the file
        file_path, document_id = await self.save_uploaded_file(file, self.jd_dir)
        
        # Parse the document
        raw_text = parse_document(file_path, file.filename)
        file_type = get_file_type(file.filename)
        
        parsed_doc = ParsedDocument(
            file_name=file.filename,
            file_type=file_type,
            raw_text=raw_text
        )
        
        logger.info(f"Job description parsed successfully: {document_id}")
        return parsed_doc, document_id

    async def parse_multiple_resumes(self, files: List[UploadFile]) -> List[tuple[ParsedDocument, str]]:
        """
        Parse multiple resume files.

        Args:
            files: List of UploadFile objects (resumes)

        Returns:
            List of tuples (ParsedDocument object, document_id)
        """
        logger.info(f"Parsing {len(files)} resume files")
        results = []
        
        for file in files:
            parsed_doc, doc_id = await self.parse_resume(file)
            results.append((parsed_doc, doc_id))
        
        logger.info(f"Successfully parsed {len(results)} resume files")
        return results


# Singleton instance
resume_parser_service = ResumeParserService()
