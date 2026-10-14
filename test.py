
import unittest
from unittest.mock import patch

from question_bank import question_bank
from skill_tree import skill_tree
from app import select_balanced_questions


class TestProjectValidation(unittest.TestCase):

    def test_every_skill_has_a_question_bank(self):
        for skill_id in skill_tree:
            with self.subTest(skill_id=skill_id):
                self.assertIn(skill_id, question_bank)
                self.assertTrue(question_bank[skill_id])

    def test_question_structure_and_answer_keys(self):
        for skill_id, questions in question_bank.items():
            with self.subTest(skill_id=skill_id):
                self.assertIn(skill_id, skill_tree)
                self.assertIsInstance(questions, list)
                self.assertGreater(len(questions), 0)

                for index, question in enumerate(questions, start=1):
                    with self.subTest(
                        skill_id=skill_id,
                        question_number=index,
                    ):
                        self.assertIsInstance(question, dict)

                        for field in (
                            "question",
                            "options",
                            "answer",
                            "concept",
                        ):
                            self.assertIn(field, question)

                        self.assertTrue(question["question"].strip())
                        self.assertIsInstance(question["options"], list)
                        self.assertEqual(len(question["options"]), 4)

                        self.assertTrue(
                            all(
                                isinstance(option, str)
                                for option in question["options"]
                            )
                        )

                        self.assertIn(
                            question["answer"],
                            ["A", "B", "C", "D"],
                        )

                        self.assertTrue(
                            any(
                                option.startswith(
                                    question["answer"] + "."
                                )
                                for option in question["options"]
                            ),
                            msg="No option matches the answer key.",
                        )

                        self.assertTrue(question["concept"].strip())

    def test_prerequisites_reference_existing_skills(self):
        for skill_id, details in skill_tree.items():
            with self.subTest(skill_id=skill_id):
                self.assertIn("prerequisites", details)

                for prerequisite in details["prerequisites"]:
                    self.assertIn(
                        prerequisite,
                        skill_tree,
                        msg=(
                            f"{skill_id} references unknown prerequisite "
                            f"{prerequisite}"
                        ),
                    )

    def test_passing_scores_are_valid_percentages(self):
        for skill_id, details in skill_tree.items():
            with self.subTest(skill_id=skill_id):
                passing_score = details.get("passing_score")
                self.assertIsInstance(passing_score, (int, float))
                self.assertGreaterEqual(passing_score, 0)
                self.assertLessEqual(passing_score, 100)

    def test_every_question_has_a_valid_skill(self):
        for skill_id in question_bank:
            with self.subTest(skill_id=skill_id):
                self.assertIn(skill_id, skill_tree)

    def test_empty_question_bank_returns_no_questions(self):
        with patch("app.question_bank", {}):
            result = select_balanced_questions("python_basics")

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
