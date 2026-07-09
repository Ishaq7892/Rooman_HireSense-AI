import os
import json
from pathlib import Path
from typing import Dict
from backend.core.logging import logger
from backend.models.schemas import StructuredResume, StructuredJobDescription
from ai.chains import extraction_chains


class ExtractionService:
    """
    Service class for extracting structured data from resumes and job descriptions.
    """

    def __init__(self):
        self.data_dir = Path("data")
        self.resumes_dir = self.data_dir / "resumes"
        self.jd_dir = self.data_dir / "job_descriptions"
        self.extraction_chains = extraction_chains
        
        logger.info("ExtractionService initialized")

    async def extract_resume_data(self, document_id: str, raw_text: str) -> StructuredResume:
        """
        Extract structured data from a resume.

        Args:
            document_id: Unique identifier for the resume
            raw_text: Raw text from the resume

        Returns:
            StructuredResume object with extracted data
        """
        try:
            logger.info(f"Extracting data for resume {document_id}")
            structured_data = self.extraction_chains.extract_resume(raw_text)
            
            # Save structured data to file (optional, for persistence)
            self._save_structured_data(
                document_id,
                structured_data.dict(),
                self.resumes_dir
            )
            
            return structured_data
        except Exception as e:
            logger.error(f"Error extracting resume data for {document_id}: {str(e)}", exc_info=True)
            raise Exception(f"Failed to extract resume data: {str(e)}")

    async def extract_job_description_data(self, document_id: str, raw_text: str) -> StructuredJobDescription:
        """
        Extract structured data from a job description.

        Args:
            document_id: Unique identifier for the job description
            raw_text: Raw text from the job description

        Returns:
            StructuredJobDescription object with extracted data
        """
        try:
            logger.info(f"Extracting data for job description {document_id}")
            structured_data = self.extraction_chains.extract_job_description(raw_text)
            
            # Save structured data to file (optional, for persistence)
            self._save_structured_data(
                document_id,
                structured_data.dict(),
                self.jd_dir
            )
            
            return structured_data
        except Exception as e:
            logger.error(f"Error extracting job description data for {document_id}: {str(e)}", exc_info=True)
            raise Exception(f"Failed to extract job description data: {str(e)}")

    def _save_structured_data(self, document_id: str, data: Dict, target_dir: Path):
        """
        Save structured data to a JSON file.

        Args:
            document_id: Unique identifier for the document
            data: Structured data to save
            target_dir: Directory to save the file
        """
        try:
            file_path = target_dir / f"{document_id}_structured.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Structured data saved to {file_path}")
        except Exception as e:
            logger.warning(f"Failed to save structured data to file: {str(e)}")

    def get_saved_structured_data(self, document_id: str, target_dir: Path) -> Dict | None:
        """
        Get saved structured data from a JSON file (if it exists).

        Args:
            document_id: Unique identifier for the document
            target_dir: Directory where the file is stored

        Returns:
            Structured data as a dictionary, or None if not found
        """
        try:
            file_path = target_dir / f"{document_id}_structured.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.warning(f"Failed to load saved structured data: {str(e)}")
            return None


# Singleton instance
extraction_service = ExtractionService()
