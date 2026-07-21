from groq import Groq

from config import GROQ_API_KEY

def generate_candidate_summary(jd_data: dict, result: dict) -> str:
    """
    Generate an AI explanation for a ranked candidate using Groq LLM,
    with a structured rule-based fallback if API key is not configured.
    """

    missing_skills = ", ".join(result["missing_skills"]) if result["missing_skills"] else "None"
    matched_skills = ", ".join(result["matched_skills"]) if result["matched_skills"] else "None"

    # Attempt Groq LLM generation if API key is available
    if GROQ_API_KEY:
        try:
            client = Groq(api_key=GROQ_API_KEY)
            prompt = f"""
    You are an experienced HR recruiter.

    A resume has already been evaluated using a deterministic NLP scoring system.

    Job Description Required Skills:
    {", ".join(jd_data.get("skills", []))}

    Resume File:
    {result["resume_file"]}

    Matched Skills:
    {matched_skills}

    Missing Skills:
    {missing_skills}

    Matched Skill Count:
    {result["matched_skill_count"]}/{result["required_skill_count"]}

    TF-IDF Similarity:
    {result["tfidf_score"]}

    Skill Match:
    {result["skill_score"]}%

    Education Score:
    {result["education_score"]}

    Final Score:
    {result["final_score"]}

    Current Recommendation:
    {result["status"]}

    IMPORTANT:
    - Use ONLY the information provided.
    - Do NOT invent skills or experience.
    - Mention missing skills if appropriate.
    - Keep the explanation concise.

    Write exactly in this format:

    Strengths:
    - ...
    - ...

    Weakness:
    - ...

    Recommendation:
    ...
    """

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            # Fall back to structured explanation if Groq API call fails
            pass

    # Deterministic Structured Fallback Summary
    strengths = []
    if result["matched_skills"]:
        strengths.append(f"Demonstrates key required competencies: {matched_skills}.")
    if result["tfidf_score"] >= 40:
        strengths.append(f"Strong overall document semantic relevance ({result['tfidf_score']}% TF-IDF match).")
    if result["education_score"] > 0:
        strengths.append("Meets academic/education background criteria.")

    if not strengths:
        strengths.append("Basic text match with job description.")

    weaknesses = []
    if result["missing_skills"]:
        weaknesses.append(f"Lacks explicitly mentioned required skills: {missing_skills}.")
    if result["tfidf_score"] < 40:
        weaknesses.append("Moderate to low keyword density match across resume sections.")
    if result["education_score"] == 0 and jd_data.get("education"):
        weaknesses.append(f"Preferred education ({jd_data.get('education').title()}) not explicitly detected.")

    if not weaknesses:
        weaknesses.append("No major skill gaps identified against job description.")

    recommendation_map = {
        "Highly Recommended": f"Candidate aligns exceptionally well with a final ATS score of {result['final_score']}%. Fast-track for technical interview.",
        "Recommended": f"Solid profile scoring {result['final_score']}%. Recommended for initial screening round.",
        "Consider": f"Profile matches partial requirements ({result['final_score']}%). Consider if secondary skillsets align with department needs.",
        "Not Recommended": f"Score of {result['final_score']}% indicates significant gaps in required core competencies."
    }

    rec_text = recommendation_map.get(result["status"], f"Candidate scored {result['final_score']}%.")

    strengths_str = "\n".join(f"- {s}" for s in strengths)
    weaknesses_str = "\n".join(f"- {w}" for w in weaknesses)

    return f"Strengths:\n{strengths_str}\n\nWeakness:\n{weaknesses_str}\n\nRecommendation:\n{rec_text}"