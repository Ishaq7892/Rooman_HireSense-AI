import unittest
from utils.jd_parser import extract_skills, extract_education


class TestJDParser(unittest.TestCase):

    def test_extract_skills(self):
        cleaned_text = "we are looking for a senior python developer with sql pandas and aws skills"
        skills = extract_skills(cleaned_text)
        self.assertIsInstance(skills, list)
        self.assertIn("python", skills)
        self.assertIn("sql", skills)

    def test_extract_education(self):
        cleaned_text = "requires a bachelor degree in computer science or related field"
        edu = extract_education(cleaned_text)
        self.assertEqual(edu, "bachelor")


if __name__ == "__main__":
    unittest.main()
