import unittest
from utils.scorer import (
    compute_tfidf_similarity,
    compute_skill_match,
    compute_education_score,
    compute_final_score,
    get_recommendation,
    score_resume,
)


class TestScorer(unittest.TestCase):

    def test_tfidf_similarity(self):
        jd = "python data science machine learning"
        resume = "python data science software engineer"
        score = compute_tfidf_similarity(jd, resume)
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_skill_match(self):
        jd_skills = ["python", "sql", "aws", "docker"]
        resume_skills = ["python", "sql", "git"]
        percentage, matched = compute_skill_match(jd_skills, resume_skills)
        self.assertEqual(percentage, 50.0)
        self.assertIn("python", matched)
        self.assertIn("sql", matched)

    def test_education_score(self):
        self.assertEqual(compute_education_score("bachelor", "bachelor"), 100)
        self.assertEqual(compute_education_score("bachelor", "master"), 0)

    def test_recommendation_thresholds(self):
        self.assertEqual(get_recommendation(90), "Highly Recommended")
        self.assertEqual(get_recommendation(75), "Recommended")
        self.assertEqual(get_recommendation(60), "Consider")
        self.assertEqual(get_recommendation(40), "Not Recommended")


if __name__ == "__main__":
    unittest.main()
