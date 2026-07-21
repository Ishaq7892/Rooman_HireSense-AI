from pathlib import Path
import re

from utils.pdf_parser import extract_text
from utils.text_cleaner import clean_text
from utils.logger import logger
from utils.skills_loader import load_skills


# ----------------------------------------------------
# Extract skills from Job Description
# ----------------------------------------------------

def extract_skills(cleaned_text: str):
    """
    Extract matching skills from the cleaned job description.

    Args:
        cleaned_text (str): Cleaned job description text.

    Returns:
        list: List of detected skills.
    """

    detected_skills = []
    skills_database = load_skills()

    for skill in skills_database:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, cleaned_text, flags=re.IGNORECASE):
            detected_skills.append(skill)

    return sorted(set(detected_skills))


# ----------------------------------------------------
# Extract education requirement
# ----------------------------------------------------

def extract_education(cleaned_text: str):
    """
    Detect the highest education requirement mentioned
    in the Job Description.
    """

    education_keywords = [
        "phd",
        "doctorate",
        "master",
        "bachelor",
        "b.tech",
        "b.e",
        "bs",
        "ba",
    ]

    for education in education_keywords:
        if education in cleaned_text:
            return education

    return ""


# ----------------------------------------------------
# Parse Job Description
# ----------------------------------------------------

def parse_job_description(file_path: str):
    """
    Parse a Job Description and extract:
    - raw text
    - cleaned text
    - skills
    - education
    """

    path = Path(file_path)

    if not path.exists():
        logger.error(f"Job Description not found: {file_path}")
        return {}

    raw_text = extract_text(file_path)

    if not raw_text:
        logger.error("Unable to read Job Description.")
        return {}

    cleaned_text = clean_text(raw_text)

    detected_skills = extract_skills(cleaned_text)

    education = extract_education(cleaned_text)

    logger.info(f"Detected {len(detected_skills)} skills from Job Description.")

    return {
        "raw_text": raw_text,
        "clean_text": cleaned_text,
        "skills": detected_skills,
        "education": education,
    }