import unittest
from utils.skills_loader import load_skills


class TestSkillsLoader(unittest.TestCase):

    def test_load_skills_returns_list(self):
        skills = load_skills()
        self.assertIsInstance(skills, list)

    def test_skills_are_loaded(self):
        skills = load_skills()
        self.assertGreater(len(skills), 0)

    def test_python_exists(self):
        skills = load_skills()
        self.assertIn("python", skills)

    def test_sql_exists(self):
        skills = load_skills()
        self.assertIn("sql", skills)

    def test_no_duplicates(self):
        skills = load_skills()
        self.assertEqual(len(skills), len(set(skills)))


if __name__ == "__main__":
    unittest.main()