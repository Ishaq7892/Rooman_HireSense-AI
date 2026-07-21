import unittest
from utils.resume_parser import parse_resume


class TestResumeParser(unittest.TestCase):

    def test_resume_parser_returns_dict(self):
        resume = parse_resume("Python SQL Machine Learning Bachelor")
        self.assertIsInstance(resume, dict)

    def test_extract_python(self):
        resume = parse_resume("Experienced Python Developer")
        self.assertIn("python", resume["skills"])

    def test_extract_sql(self):
        resume = parse_resume("Worked extensively with SQL databases.")
        self.assertIn("sql", resume["skills"])

    def test_extract_multiple_skills(self):
        resume = parse_resume("Python SQL Docker AWS")
        self.assertGreaterEqual(len(resume["skills"]), 4)

    def test_extract_education(self):
        resume = parse_resume("Bachelor of Engineering in Computer Science")
        self.assertEqual(resume["education"], "bachelor")


if __name__ == "__main__":
    unittest.main()