"""
scorer.py

Computes resume relevance scores against a job description.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ----------------------------------------------------
# TF-IDF Similarity
# ----------------------------------------------------

def compute_tfidf_similarity(jd_text: str, resume_text: str) -> float:
    """
    Compute cosine similarity between Job Description
    and Resume using TF-IDF.

    Returns:
        float: Similarity score (0-100)
    """

    vectorizer = TfidfVectorizer(stop_words="english")

    tfidf_matrix = vectorizer.fit_transform(
        [jd_text, resume_text]
    )

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    return round(float(similarity * 100), 2)


# ----------------------------------------------------
# Skill Matching
# ----------------------------------------------------

def compute_skill_match(
    jd_skills: list,
    resume_skills: list,
):
    """
    Compare JD skills against extracted resume skills.
    """

    if not jd_skills:
        return 100.0, []

    matched = []

    resume_skill_set = set(resume_skills)

    for skill in jd_skills:
        if skill in resume_skill_set:
            matched.append(skill)

    percentage = (
        len(matched) / len(jd_skills)
    ) * 100

    return round(percentage, 2), matched


# ----------------------------------------------------
# Education Matching
# ----------------------------------------------------

def compute_education_score(
    jd_education: str,
    resume_education: str,
):
    """
    Compare education requirements.
    """

    if not jd_education:
        return 100

    return (
        100
        if jd_education == resume_education
        else 0
    )


# ----------------------------------------------------
# Final Weighted Score
# ----------------------------------------------------

def compute_final_score(
    tfidf_score,
    skill_score,
    education_score,
):
    """
    Compute final ATS score.

    Weighting:

    Skills      : 50%
    TF-IDF      : 40%
    Education   : 10%
    """

    final = (

        skill_score * 0.50 +

        tfidf_score * 0.40 +

        education_score * 0.10

    )

    return round(final, 2)


# ----------------------------------------------------
# Recommendation
# ----------------------------------------------------

def get_recommendation(score: float):

    if score >= 85:
        return "Highly Recommended"

    if score >= 70:
        return "Recommended"

    if score >= 50:
        return "Consider"

    return "Not Recommended"


# ----------------------------------------------------
# Main Scoring Function
# ----------------------------------------------------

def score_resume(
    jd_data: dict,
    resume_name: str,
    resume_data: dict,
):
    """
    Score a resume against a Job Description.
    """

    tfidf = compute_tfidf_similarity(
        jd_data["clean_text"],
        resume_data["clean_text"],
    )

    skill_score, matched = compute_skill_match(
        jd_data["skills"],
        resume_data["skills"],
    )

    education = compute_education_score(
        jd_data["education"],
        resume_data["education"],
    )

    final = compute_final_score(
        tfidf,
        skill_score,
        education,
    )

    missing = [
        skill
        for skill in jd_data["skills"]
        if skill not in matched
    ]

    return {

        "resume_file": resume_name,

        "tfidf_score": tfidf,

        "skill_score": skill_score,

        "education_score": education,

        "matched_skills": matched,

        "missing_skills": missing,

        "matched_skill_count": len(matched),

        "required_skill_count": len(jd_data["skills"]),

        "final_score": final,

        "status": get_recommendation(final),

    }