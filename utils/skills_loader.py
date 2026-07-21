"""
skills_loader.py

Loads and caches the project's skills database.
"""

from functools import lru_cache
from pathlib import Path

from utils.logger import logger

SKILLS_FILE = Path("sample_data/skills.txt")


@lru_cache(maxsize=1)
def load_skills():
    """
    Load skills from sample_data/skills.txt.

    The skills are loaded only once and then cached for the
    lifetime of the application.

    Returns:
        list[str]: Sorted list of unique skills in lowercase.
    """

    if not SKILLS_FILE.exists():
        logger.error(f"Skills file not found: {SKILLS_FILE}")
        return []

    try:
        skills = set()

        with SKILLS_FILE.open("r", encoding="utf-8") as file:

            for line in file:

                skill = line.strip().lower()

                # Ignore blank lines
                if not skill:
                    continue

                # Ignore comments
                if skill.startswith("#"):
                    continue

                skills.add(skill)

        skills = sorted(
            skills,
            key=len,
            reverse=True
        )

        logger.info(
            f"Loaded {len(skills)} skills from {SKILLS_FILE}"
        )

        return skills

    except Exception as e:
        logger.exception(f"Error loading skills: {e}")
        return []