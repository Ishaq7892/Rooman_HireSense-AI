"""
resume_parser.py

Parses cleaned resume text and extracts structured information
such as skills and education.
"""

import re

from utils.skills_loader import load_skills


def extract_skills(cleaned_text: str):
    """
    Extract skills from a cleaned resume using the shared skills database.

    Args:
        cleaned_text (str): Cleaned resume text.

    Returns:
        list: List of detected skills.
    """

    skills_database = load_skills()
    detected_skills = []

    for skill in skills_database:
        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, cleaned_text, flags=re.IGNORECASE):
            detected_skills.append(skill)

    return sorted(set(detected_skills))


def extract_education(cleaned_text: str):
    """
    Detect the highest education level mentioned
    in the resume.
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
        if education in cleaned_text.lower():
            return education

    return ""


def parse_resume(cleaned_text: str):
    """
    Parse a cleaned resume and return structured information.

    Returns:
        dict
    """

    return {
        "skills": extract_skills(cleaned_text),
        "education": extract_education(cleaned_text),
        "clean_text": cleaned_text,
    }