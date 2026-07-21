"""
pdf_parser.py

Handles text extraction from PDF, DOCX, and TXT resume files.
"""

from pathlib import Path

import fitz  # PyMuPDF
from docx import Document

from utils.logger import logger


def read_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: Extracted text.
    """
    try:
        document = fitz.open(file_path)
        text = ""

        for page in document:
            text += page.get_text()

        document.close()

        logger.info(f"Successfully read PDF: {file_path}")
        return text

    except Exception as e:
        logger.error(f"Failed to read PDF {file_path}: {e}")
        return ""


def read_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file.

    Args:
        file_path (str): Path to the DOCX file.

    Returns:
        str: Extracted text.
    """
    try:
        document = Document(file_path)

        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

        logger.info(f"Successfully read DOCX: {file_path}")
        return text

    except Exception as e:
        logger.error(f"Failed to read DOCX {file_path}: {e}")
        return ""


def read_txt(file_path: str) -> str:
    """
    Read a plain text resume.

    Args:
        file_path (str): Path to TXT file.

    Returns:
        str: File contents.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

        logger.info(f"Successfully read TXT: {file_path}")
        return text

    except Exception as e:
        logger.error(f"Failed to read TXT {file_path}: {e}")
        return ""


def extract_text(file_path: str) -> str:
    """
    Detect file type and extract text.

    Supports:
        - PDF
        - DOCX
        - TXT

    Args:
        file_path (str): Resume file path.

    Returns:
        str: Extracted text.
    """

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return read_pdf(file_path)

    elif extension == ".docx":
        return read_docx(file_path)

    elif extension == ".txt":
        return read_txt(file_path)

    else:
        logger.warning(f"Unsupported file format: {extension}")
        return ""