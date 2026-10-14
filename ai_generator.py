
import json
import time

import streamlit as st
from google import genai


def generate_dynamic_question(skill_name, concept_name):
    """Generate one AI-powered multiple-choice practice question."""

    api_key = st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Gemini API key is not configured.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
    Create one beginner-level multiple-choice question.

    Skill: {skill_name}
    Concept: {concept_name}

    Return a JSON object with these fields:
    - question: the question text
    - options: exactly four strings, formatted as A. ..., B. ..., C. ..., D. ...
    - answer: the correct letter A, B, C, or D
    - concept: exactly {concept_name}
    - explanation: a short explanation of the correct answer

    Ensure exactly one answer is correct.
    """

    response = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            break

        except Exception as error:
            if "503" not in str(error) or attempt == 2:
                raise

            time.sleep(2 ** (attempt + 1))

    if response is None or not response.text:
        raise ValueError("Gemini returned an empty response.")

    question = json.loads(response.text)

    # Validate the generated question.
    if not isinstance(question, dict):
        raise ValueError("Gemini did not return a JSON object.")

    if not isinstance(question.get("question"), str):
        raise ValueError("Invalid question text.")

    if not isinstance(question.get("options"), list):
        raise ValueError("Invalid answer options.")

    if len(question["options"]) != 4:
        raise ValueError("Expected exactly four options.")

    if not all(isinstance(option, str) for option in question["options"]):
        raise ValueError("Every answer option must be a string.")

    if question.get("answer") not in {"A", "B", "C", "D"}:
        raise ValueError("Invalid correct-answer letter.")

    if question.get("concept") != concept_name:
        raise ValueError("Generated concept does not match.")

    if not isinstance(question.get("explanation"), str):
        raise ValueError("Missing answer explanation.")

    return question
