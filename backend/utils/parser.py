import os
from pathlib import Path
from typing import BinaryIO
import logging
import fitz  # PyMuPDF for PDFs
from docx import Document  # python-docx for DOCX
from backend.core.logging import logger


def parse_pdf(file_path: str) -> str:
    """
    Parse a PDF file and extract raw text.

    Args:
        file_path: Path to the PDF file

    Returns:
        Extracted raw text as string

    Raises:
        Exception: If there's an error parsing the PDF
    """
    try:
        logger.info(f"Parsing PDF file: {file_path}")
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        logger.info(f"Successfully parsed PDF file: {file_path}")
        return text.strip()
    except Exception as e:
        logger.error(f"Error parsing PDF file {file_path}: {str(e)}", exc_info=True)
        raise Exception(f"Failed to parse PDF: {str(e)}")


def parse_docx(file_path: str) -> str:
    """
    Parse a DOCX file and extract raw text.

    Args:
        file_path: Path to the DOCX file

    Returns:
        Extracted raw text as string

    Raises:
        Exception: If there's an error parsing the DOCX
    """
    try:
        logger.info(f"Parsing DOCX file: {file_path}")
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        logger.info(f"Successfully parsed DOCX file: {file_path}")
        return text.strip()
    except Exception as e:
        logger.error(f"Error parsing DOCX file {file_path}: {str(e)}", exc_info=True)
        raise Exception(f"Failed to parse DOCX: {str(e)}")


def parse_txt(file_path: str) -> str:
    """
    Parse a TXT file and extract raw text.

    Args:
        file_path: Path to the TXT file

    Returns:
        Extracted raw text as string

    Raises:
        Exception: If there's an error reading the TXT file
    """
    try:
        logger.info(f"Parsing TXT file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        logger.info(f"Successfully parsed TXT file: {file_path}")
        return text.strip()
    except Exception as e:
        logger.error(f"Error parsing TXT file {file_path}: {str(e)}", exc_info=True)
        raise Exception(f"Failed to parse TXT: {str(e)}")


def get_file_type(file_name: str) -> str:
    """
    Determine the file type from the file extension.

    Args:
        file_name: Name of the file

    Returns:
        File type: "pdf", "docx", or "txt"

    Raises:
        ValueError: If the file type is not supported
    """
    ext = Path(file_name).suffix.lower().lstrip(".")
    if ext not in ["pdf", "docx", "txt"]:
        logger.error(f"Unsupported file type: {ext} for file {file_name}")
        raise ValueError(f"Unsupported file type: {ext}. Supported types: pdf, docx, txt")
    return ext


def parse_document(file_path: str, file_name: str) -> str:
    """
    Parse a document (PDF/DOCX/TXT) and extract raw text.

    Args:
        file_path: Path to the document file
        file_name: Original name of the file

    Returns:
        Extracted raw text as string
    """
    file_type = get_file_type(file_name)
    
    if file_type == "pdf":
        return parse_pdf(file_path)
    elif file_type == "docx":
        return parse_docx(file_path)
    elif file_type == "txt":
        return parse_txt(file_path)
    else:
        # This should not happen due to get_file_type check
        raise ValueError(f"Unsupported file type: {file_type}")
