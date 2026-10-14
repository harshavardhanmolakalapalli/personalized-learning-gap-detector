import json
import unittest
from unittest.mock import Mock, patch

from ai_generator import generate_dynamic_question


class TestAIGenerator(unittest.TestCase):
    @patch("ai_generator.genai.Client")
    @patch("ai_generator.st.secrets", new={"GEMINI_API_KEY": "test-key"})
    def test_returns_valid_generated_question(self, mock_client_class):
        expected = {
            "question": "What does range(3) produce?",
            "options": ["A. 1, 2, 3", "B. 0, 1, 2", "C. 0, 1, 2, 3", "D. 3"],
            "answer": "B",
            "concept": "loops",
            "explanation": "range(3) starts at zero and stops before three.",
        }
        response = Mock()
        response.text = json.dumps(expected)
        mock_client = mock_client_class.return_value
        mock_client.models.generate_content.return_value = response

        result = generate_dynamic_question("Python Basics", "loops")

        self.assertEqual(result, expected)
        mock_client.models.generate_content.assert_called_once()

    @patch("ai_generator.genai.Client")
    @patch("ai_generator.st.secrets", new={"GEMINI_API_KEY": "test-key"})
    def test_rejects_invalid_option_count(self, mock_client_class):
        response = Mock()
        response.text = json.dumps({
            "question": "Question?",
            "options": ["A. One", "B. Two"],
            "answer": "A",
            "concept": "loops",
            "explanation": "Explanation.",
        })
        mock_client_class.return_value.models.generate_content.return_value = response

        with self.assertRaisesRegex(ValueError, "four options"):
            generate_dynamic_question("Python Basics", "loops")


if __name__ == "__main__":
    unittest.main(verbosity=2)
