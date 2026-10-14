import json
import random
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from question_bank import question_bank
from skill_tree import skill_tree
from recommendation import learning_resources
from ai_generator import generate_dynamic_question


# =========================================================
# 1. CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Personalized Learning Gap Detector",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
RESULTS_FILE = BASE_DIR / "assessment_results.json"
QUESTIONS_PER_ASSESSMENT = 6
WEAK_CONCEPT_THRESHOLD = 70


# =========================================================
# 2. DATA HELPERS
# =========================================================

def load_assessment_history():
    """Load assessment history without crashing on a missing file."""
    if not RESULTS_FILE.exists():
        return []

    try:
        with RESULTS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            st.warning(
                "assessment_results.json must contain a JSON list. "
                "The dashboard is showing an empty history."
            )
            return []

        return [item for item in data if isinstance(item, dict)]

    except (json.JSONDecodeError, OSError) as error:
        st.error(f"Could not read assessment history: {error}")
        return []


def save_assessment_result(result):
    """Append one assessment record using the existing project schema."""
    history = load_assessment_history()
    history.append(result)

    try:
        with RESULTS_FILE.open("w", encoding="utf-8") as file:
            json.dump(history, file, indent=4, ensure_ascii=False)
        return True
    except OSError as error:
        st.error(f"Could not save assessment result: {error}")
        return False


def get_passed_skill_ids(history):
    """A skill is demonstrated if it has been passed at least once."""
    return{
        item.get("skill_id")
        for item in history
        if item.get("skill_id") in skill_tree
        and item.get("status") == "Demonstrated"
    }


def get_available_skill_ids(history):
    """Return skills whose prerequisites have been demonstrated."""
    passed = get_passed_skill_ids(history)
    available = []

    for skill_id, details in skill_tree.items():
        if skill_id not in question_bank or not question_bank[skill_id]:
            continue

        prerequisites = details.get("prerequisites", [])
        if all(prerequisite in passed for prerequisite in prerequisites):
            available.append(skill_id)

    return available


def select_balanced_questions(skill_id):
    """Choose up to six questions, spreading them across concepts."""
    bank = question_bank.get(skill_id, [])
    grouped = {}

    for question in bank:
        grouped.setdefault(question["concept"], []).append(question)

    concepts = list(grouped)
    random.shuffle(concepts)

    selected = []
    target = min(QUESTIONS_PER_ASSESSMENT, len(bank))

    while len(selected) < target:
        added_question = False
        for concept in concepts:
            remaining = [
                question
                for question in grouped[concept]
                if question not in selected
            ]
            if remaining:
                selected.append(random.choice(remaining))
                added_question = True
                if len(selected) >= target:
                    break
        if not added_question:
            break

    return selected


def calculate_result(skill_id, questions, answers):
    """Score answers and return a record compatible with assignment.py."""
    if len(questions) != len(answers):
        raise ValueError(
            "The number of answers must match the number of questions."
        )

    skill = skill_tree[skill_id]
    score = 0
    concept_results = {}

    for index, question in enumerate(questions):
        concept = question["concept"]
        concept_results.setdefault(
            concept, {"attempted": 0, "correct": 0}
        )
        concept_results[concept]["attempted"] += 1

        if answers[index] == question["answer"]:
            score += 1
            concept_results[concept]["correct"] += 1

    total_questions = len(questions)
    percentage = (score / total_questions * 100) if total_questions else 0
    passed = percentage >= skill["passing_score"]

    weak_concepts = []
    for concept, stats in concept_results.items():
        accuracy = stats["correct"] / stats["attempted"] * 100
        if accuracy < WEAK_CONCEPT_THRESHOLD:
            weak_concepts.append(concept)

    return {
        "skill_id": skill_id,
        "skill_name": skill["name"],
        "score": score,
        "total_questions": total_questions,
        "percentage": round(percentage, 1),
        "passing_score": skill["passing_score"],
        "status": "Demonstrated" if passed else "Needs improvement",
        "date": datetime.now().isoformat(timespec="seconds"),
        "concept_results": concept_results,
        "weak_concepts": weak_concepts,
    }


def get_skill_name(skill_id):
    return skill_tree.get(skill_id, {}).get("name", skill_id)


# =========================================================
# 3. LOAD DATA AND SIDEBAR
# =========================================================

history = load_assessment_history()
passed_skill_ids = get_passed_skill_ids(history)
available_skill_ids = get_available_skill_ids(history)

st.sidebar.title("🎯 Learning Platform")
st.sidebar.caption("Understand your gaps. Improve your skills.")

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Skill Assessment", "Progress Dashboard", "Learning Path"],
)

st.sidebar.divider()
st.sidebar.caption(f"Skills in skill tree: {len(skill_tree)}")


# =========================================================
# 4. HOME
# =========================================================

if page == "Home":
    st.title("🎯 Personalized Learning Gap Detector")
    st.write(
        "Identify your learning gaps, improve your skills, "
        "and follow a personalized learning path."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Available Skills", len(skill_tree))
    with col2:
        st.metric("Assessments Completed", len(history))
    with col3:
        st.metric("Skills Demonstrated", len(passed_skill_ids))

    st.divider()
    st.subheader("How it works")

    left, middle, right = st.columns(3)
    with left:
        st.markdown("### 1. Assess")
        st.write("Answer questions about a skill you are eligible to study.")
    with middle:
        st.markdown("### 2. Identify gaps")
        st.write("Review your score and the concepts that need more practice.")
    with right:
        st.markdown("### 3. Progress")
        st.write("Demonstrate prerequisite skills to unlock the next stage.")

    st.subheader("Latest assessments")
    if history:
        recent = history[-5:][::-1]
        rows = [
            {
                "Skill": item.get("skill_name", get_skill_name(item.get("skill_id", ""))),
                "Score": f"{item.get('score', '?')}/{item.get('total_questions', '?')}",
                "Percentage": item.get("percentage", "—"),
                "Status": item.get("status", "Unknown"),
                "Date": item.get("date", "—"),
            }
            for item in recent
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No assessment history yet. Start your first assessment from the sidebar.")


# =========================================================
# 5. SKILL ASSESSMENT — ANSWER QUESTIONS IN THE BROWSER
# =========================================================

elif page == "Skill Assessment":
    st.title("📝 Skill Assessment")
    st.write(
        "Choose an available skill, answer the questions, "
        "and submit your assessment."
    )

    if not available_skill_ids:
        st.success(
            "No skills are currently available. You may have demonstrated "
            "all skills with available questions."
        )
    else:
        options = {
            f"{get_skill_name(skill_id)}": skill_id
            for skill_id in available_skill_ids
        }

        selected_label = st.selectbox(
            "Choose a skill",
            list(options.keys()),
            key="selected_skill_label",
        )
        selected_skill_id = options[selected_label]
        selected_skill = skill_tree[selected_skill_id]

        st.caption(
            f"Passing score: {selected_skill['passing_score']}% · "
            f"Questions per attempt: "
            f"{min(QUESTIONS_PER_ASSESSMENT, len(question_bank[selected_skill_id]))}"
        )

        if st.button("Start / Restart Assessment", type="primary"):
            st.session_state["active_assessment"] = {
                "skill_id": selected_skill_id,
                "questions": select_balanced_questions(selected_skill_id),
                "token": datetime.now().isoformat(timespec="microseconds"),
            }
            st.session_state.pop("assessment_submitted", None)
            st.rerun()

        assessment = st.session_state.get("active_assessment")

        if assessment and assessment["skill_id"] == selected_skill_id:
            questions = assessment["questions"]
            st.divider()
            st.subheader(selected_skill["name"])

            with st.form(key=f"assessment_form_{assessment['token']}"):
                answers = []

                for index, question in enumerate(questions):
                    st.markdown(f"**Question {index + 1} of {len(questions)}**")
                    st.write(question["question"])

                    chosen_option = st.radio(
                        f"Select your answer for question {index + 1}",
                        question["options"],
                        index=None,
                        key=f"answer_{assessment['token']}_{index}",
                        label_visibility="collapsed",
                    )
                    answers.append(chosen_option)

                submitted = st.form_submit_button(
                    "Submit Assessment",
                    type="primary",
                )

            if submitted:
                if any(answer is None for answer in answers):
                    st.error("Please answer every question before submitting.")
                else:
                    answer_letters = [
                        answer.split(".", 1)[0].strip()
                        for answer in answers
                    ]
                    result = calculate_result(
                        selected_skill_id,
                        questions,
                        answer_letters,
                    )

                    if save_assessment_result(result):
                        st.session_state["last_assessment_result"] = result
                        st.session_state.pop("active_assessment", None)
                        st.rerun()

        latest_result = st.session_state.get("last_assessment_result")
        if latest_result:
            st.divider()
            st.subheader("Latest assessment result")
            result_col1, result_col2, result_col3 = st.columns(3)

            with result_col1:
                st.metric(
                    "Score",
                    f"{latest_result['score']}/{latest_result['total_questions']}",
                )
            with result_col2:
                st.metric("Percentage", f"{latest_result['percentage']:.1f}%")
            with result_col3:
                st.metric("Result", latest_result["status"])

            if latest_result["status"] == "Demonstrated":
                st.success("Well done! You met the passing threshold.")
            else:
                st.warning("Review the weak concepts and try again.")

            if latest_result["weak_concepts"]:
                st.markdown("### 📚 Personalized Learning Recommendations")

                for concept in latest_result["weak_concepts"]:
                    stats = latest_result["concept_results"][concept]
                    accuracy = stats["correct"] / stats["attempted"] * 100

                    st.markdown(f"#### {concept.replace('_', ' ').title()}")
                    st.write(f"Current accuracy: {accuracy:.0f}%")

                    resource = learning_resources.get(concept)
                    if resource:
                        st.write(f"**Topic:** {resource['topic']}")
                        st.write(f"**Recommended action:** {resource['action']}")
                        st.write(f"**Practice exercise:** {resource['practice']}")
                    else:
                        st.info(
                            "No specific learning resource is available "
                            "for this concept yet."
                        )

                    # Optional AI practice for concepts missed in this assessment.
                    practice_key = f"ai_practice_{latest_result['skill_id']}_{concept}"
                    answer_key = f"ai_practice_answer_{latest_result['skill_id']}_{concept}"
                    submitted_key = f"ai_practice_submitted_{latest_result['skill_id']}_{concept}"

                    with st.expander(
                        f"✨ Generate an AI practice question: {concept.replace('_', ' ').title()}"
                    ):
                        if st.button(
                            "Generate new question",
                            key=f"generate_{practice_key}",
                        ):
                            try:
                                with st.spinner("Generating a new practice question..."):
                                    generated_question = generate_dynamic_question(
                                        latest_result["skill_name"],
                                        concept,
                                    )
                                st.session_state[practice_key] = generated_question
                                st.session_state.pop(answer_key, None)
                                st.session_state.pop(submitted_key, None)
                            except Exception as error:
                                st.error(
                                    "Could not generate a question. Check your "
                                    "internet connection, Gemini model availability, "
                                    "API quota, and API key configuration."
                                )
                                st.caption(f"Technical details: {type(error).__name__}: {error}")

                        generated_question = st.session_state.get(practice_key)

                        if generated_question:
                            st.write(generated_question["question"])
                            selected_option = st.radio(
                                "Choose your answer",
                                generated_question["options"],
                                index=None,
                                key=answer_key,
                            )

                            if st.button(
                                "Check answer",
                                key=f"check_{practice_key}",
                            ):
                                if selected_option is None:
                                    st.warning("Select an answer before checking it.")
                                else:
                                    st.session_state[submitted_key] = selected_option

                            submitted_answer = st.session_state.get(submitted_key)
                            if submitted_answer is not None:
                                chosen_letter = submitted_answer.split(".", 1)[0].strip()
                                if chosen_letter == generated_question["answer"]:
                                    st.success("Correct! Nice work.")
                                else:
                                    st.error(
                                        f"Not quite. The correct answer is "
                                        f"{generated_question['answer']}."
                                    )
                                st.info(generated_question["explanation"])

                    st.divider()
            else:
                st.success("No weak concepts were detected in this attempt.")


# =========================================================
# 6. PROGRESS DASHBOARD
# =========================================================

elif page == "Progress Dashboard":
    st.title("📊 Progress Dashboard")

    if not history:
        st.info("No assessment data yet. Complete an assessment to populate this page.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Assessments Completed", len(history))
        with col2:
            st.metric("Skills Demonstrated", len(passed_skill_ids))
        with col3:
            completion = len(passed_skill_ids) / len(skill_tree) * 100 if skill_tree else 0
            st.metric("Skill Completion", f"{completion:.1f}%")

        df = pd.DataFrame(history)

        if "status" in df.columns:
            st.subheader("Assessment outcomes")
            st.bar_chart(df["status"].fillna("Unknown").value_counts())

        if "percentage" in df.columns:
            df["percentage"] = pd.to_numeric(df["percentage"], errors="coerce")
            st.subheader("Score history")
            score_df = df[["percentage"]].dropna().reset_index(drop=True)
            if not score_df.empty:
                st.line_chart(score_df)

        st.subheader("Skill summary")
        summary_rows = []

        for skill_id, details in skill_tree.items():
            attempts = [
                item for item in history
                if item.get("skill_id") == skill_id
            ]

            scores = []
            for item in attempts:
                try:
                    scores.append(float(item.get("percentage", 0)))
                except (TypeError, ValueError):
                    continue

            first_score = scores[0] if scores else None
            latest_score = scores[-1] if scores else None
            improvement = (
                round(latest_score - first_score, 1)
                if scores else None
            )
            best_score = max(scores) if scores else None

            summary_rows.append(
                {
                    "Skill": details["name"],
                    "Attempts": len(attempts),
                    "First score (%)": first_score,
                    "Latest score (%)": latest_score,
                    "Improvement (pp)": improvement,
                    "Best score (%)": best_score,
                    "Status": (
                        "Demonstrated"
                        if skill_id in passed_skill_ids
                        else "Not demonstrated"
                    ),
                }
            )

        st.dataframe(
            pd.DataFrame(summary_rows),
            use_container_width=True,
            hide_index=True,
        )

        # Stage 20: Learning Progress Insights
        st.subheader("Learning Progress Insights")

        skill_options = {
            skill_id: details["name"]
            for skill_id, details in skill_tree.items()
        }

        if not skill_options:
            st.info("No skills are configured yet.")
        else:
            selected_skill_id = st.selectbox(
                "Choose a skill to review",
                options=list(skill_options.keys()),
                format_func=lambda skill_id: skill_options[skill_id],
                key="progress_insights_skill",
            )

            skill_attempts = [
                item
                for item in history
                if item.get("skill_id") == selected_skill_id
                and item.get("percentage") is not None
            ]

            # Ignore malformed scores rather than breaking the dashboard.
            valid_attempts = []
            for item in skill_attempts:
                try:
                    score_value = float(item["percentage"])
                except (TypeError, ValueError):
                    continue
                valid_attempts.append((item, score_value))

            if not valid_attempts:
                st.info(
                    "No assessment scores are available for this skill yet."
                )
            elif len(valid_attempts) == 1:
                latest_score = valid_attempts[-1][1]
                st.metric("Latest score", f"{latest_score:.1f}%")
                st.info(
                    "This is the first recorded score for this skill. "
                    "Complete another assessment to compare your progress."
                )
            else:
                previous_score = valid_attempts[-2][1]
                latest_score = valid_attempts[-1][1]
                improvement = latest_score - previous_score

                progress_col1, progress_col2, progress_col3 = st.columns(3)
                progress_col1.metric(
                    "Previous score",
                    f"{previous_score:.1f}%",
                )
                progress_col2.metric(
                    "Latest score",
                    f"{latest_score:.1f}%",
                )
                progress_col3.metric(
                    "Change",
                    f"{improvement:+.1f} pp",
                )

                if improvement > 0:
                    st.success(
                        f"Your score improved by {improvement:.1f} "
                        "percentage points compared with your previous "
                        "attempt. Keep practising!"
                    )
                elif improvement < 0:
                    st.warning(
                        f"Your score decreased by {abs(improvement):.1f} "
                        "percentage points. Review the concepts you find "
                        "difficult before your next attempt."
                    )
                else:
                    st.info(
                        "Your score stayed the same. Practise your weak "
                        "concepts and try another assessment."
                    )

        st.subheader("Full assessment history")
        display_columns = [
            column for column in
            ["skill_name", "skill_id", "score", "total_questions",
             "percentage", "passing_score", "status", "date"]
            if column in df.columns
        ]
        st.dataframe(
            df[display_columns] if display_columns else df,
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# 7. LEARNING PATH
# =========================================================

elif page == "Learning Path":
    st.title("🧭 Personalized Learning Path")
    st.write(
        "The sequence below follows the prerequisites defined in skill_tree.py."
    )

    for skill_id, details in skill_tree.items():
        prerequisites = details.get("prerequisites", [])
        demonstrated = skill_id in passed_skill_ids
        ready = all(prerequisite in passed_skill_ids for prerequisite in prerequisites)

        if demonstrated:
            status = "✅ Demonstrated"
        elif ready:
            status = "🟢 Ready to assess"
        else:
            status = "🔒 Prerequisites pending"

        with st.expander(f"{details['name']} — {status}"):
            st.write(f"**Passing score:** {details.get('passing_score', 80)}%")

            if prerequisites:
                names = [get_skill_name(prerequisite) for prerequisite in prerequisites]
                st.write("**Prerequisites:** " + ", ".join(names))
            else:
                st.write("**Prerequisites:** None")

            attempts = [
                item for item in history
                if item.get("skill_id") == skill_id
            ]
            if attempts:
                latest = attempts[-1]
                st.write(
                    f"**Latest result:** {latest.get('percentage', '—')}% "
                    f"— {latest.get('status', 'Unknown')}"
                )
                weak_concepts = latest.get("weak_concepts", [])
                if weak_concepts:
                    st.write(
                        "**Review:** "
                        + ", ".join(
                            concept.replace("_", " ").title()
                            for concept in weak_concepts
                        )
                    )

    st.divider()
    next_skills = [
        get_skill_name(skill_id)
        for skill_id in available_skill_ids
        if skill_id not in passed_skill_ids
    ]

    if next_skills:
        st.info("Your currently available skills: " + ", ".join(next_skills))
    else:
        st.success("No new skill is currently unlocked. Review previous results or complete available skills.")


# =========================================================
# 8. FOOTER
# =========================================================

st.divider()
st.caption(
    "Personalized Learning Gap Detector | Python · Streamlit · Learning Analytics"
)
