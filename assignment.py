import json
import random
from datetime import datetime
from skill_tree import skill_tree
from question_bank import question_bank
from recommendation import learning_resources
from dashboard import show_dashboard


# ==========================================
# 1. CONFIGURATION AND SKILL SELECTION
# ==========================================

number_to_ask = 6
file_name = "assessment_results.json"
weak_concept_threshold = 70

# Load previous assessment history.
try:
    with open(file_name, "r", encoding="utf-8") as file:
        results = json.load(file)

    if not isinstance(results, list):
        raise ValueError("Assessment history must be a JSON list.")

except FileNotFoundError:
    results = []

# Record skills that have been passed at least once.
passed_skill_ids = {
    result.get("skill_id")
    for result in results
    if isinstance(result, dict)
    and result.get("status") == "Demonstrated"
}

# Find skills whose prerequisites have been completed and have questions.
available_skill_ids = []

for sid, details in skill_tree.items():
    if sid not in question_bank or not question_bank[sid]:
        continue

    prerequisites = details["prerequisites"]

    if all(
        prerequisite in passed_skill_ids
        for prerequisite in prerequisites
    ):
        available_skill_ids.append(sid)

if not available_skill_ids:
    raise ValueError("No skills with available questions or met prerequisites were found.")

print("\n" + "=" * 45)
print("      PERSONALIZED LEARNING SYSTEM")
print("=" * 45)
print("\nChoose a skill to assess:\n")

for index, sid in enumerate(available_skill_ids, start=1):
    print(f"{index}. {skill_tree[sid]['name']}")

while True:
    choice = input("\nEnter the skill number: ").strip()

    if choice.isdigit():
        choice_number = int(choice)

        if 1 <= choice_number <= len(available_skill_ids):
            skill_id = available_skill_ids[choice_number - 1]
            break

    print("Invalid choice. Select a number from the menu.")

# Load the selected skill and its questions.
skill = skill_tree[skill_id]
available_questions = question_bank[skill_id]


# ==========================================
# 2. VALIDATE QUESTION BANK
# ==========================================

if not isinstance(available_questions, list):
    raise TypeError("The question bank must contain a list of questions.")

if not available_questions:
    raise ValueError(f"The question bank for '{skill_id}' is empty.")

for index, question in enumerate(available_questions, start=1):

    if not isinstance(question, dict):
        raise TypeError(
            f"Question {index} must be a dictionary."
        )

    required_fields = ["question", "options", "answer", "concept"]

    for field in required_fields:
        if field not in question:
            raise ValueError(
                f"Question {index} is missing '{field}'."
            )

    if not isinstance(question["options"], list):
        raise TypeError(
            f"Options for question {index} must be a list."
        )

    if len(question["options"]) != 4:
        raise ValueError(
            f"Question {index} must have four options."
        )

    if not all(
        isinstance(option, str)
        for option in question["options"]
    ):
        raise TypeError(
            f"All options for question {index} must be strings."
        )

    if question["answer"] not in ["A", "B", "C", "D"]:
        raise ValueError(
            f"Question {index} has an invalid answer key."
        )

    if not any(
        option.startswith(question["answer"] + ".")
        for option in question["options"]
    ):
        raise ValueError(
            f"Question {index} has no option matching its answer key."
        )


# ==========================================
# 3. SELECT QUESTIONS BY CONCEPT
# ==========================================

questions_by_concept = {}

for question in available_questions:
    concept = question["concept"]

    if concept not in questions_by_concept:
        questions_by_concept[concept] = []

    questions_by_concept[concept].append(question)

concepts = list(questions_by_concept.keys())
random.shuffle(concepts)

questions = []
target_count = min(number_to_ask, len(available_questions))

while len(questions) < target_count:
    added_question = False

    for concept in concepts:
        remaining = [
            question
            for question in questions_by_concept[concept]
            if question not in questions
        ]

        if remaining:
            questions.append(random.choice(remaining))
            added_question = True

            if len(questions) >= target_count:
                break

    if not added_question:
        break

# These MUST be outside the while loop.
number_of_questions = len(questions)
score = 0
concept_results = {}


# ==========================================
# 4. RUN ASSESSMENT
# ==========================================

print("=" * 45)
print(f"  {skill['name'].upper()} ASSESSMENT")
print("=" * 45)

print(f"Questions in this attempt: {number_of_questions}")
print("Enter A, B, C, or D.")

for index, question in enumerate(questions, start=1):

    print(f"\nQuestion {index}: {question['question']}")

    for option in question["options"]:
        print(option)

    while True:
        user_answer = input(
            "Your answer (A/B/C/D): "
        ).strip().upper()

        if user_answer in ["A", "B", "C", "D"]:
            break

        print("Invalid input. Enter A, B, C, or D.")

    concept = question["concept"]

    if concept not in concept_results:
        concept_results[concept] = {
            "attempted": 0,
            "correct": 0
        }

    concept_results[concept]["attempted"] += 1

    if user_answer == question["answer"]:
        print("Correct!")
        score += 1
        concept_results[concept]["correct"] += 1
    else:
        print("Incorrect.")


# ==========================================
# 5. CALCULATE RESULTS
# ==========================================

total_questions = len(questions)
percentage = (score / total_questions) * 100

passed = percentage >= skill["passing_score"]

status = (
    "Demonstrated"
    if passed
    else "Needs improvement"
)

weak_concepts = []

for concept, result in concept_results.items():
    accuracy = (
        result["correct"] / result["attempted"]
    ) * 100

    if accuracy < weak_concept_threshold:
        weak_concepts.append(concept)

assessment_result = {
    "skill_id": skill_id,
    "skill_name": skill["name"],
    "score": score,
    "total_questions": total_questions,
    "percentage": round(percentage, 1),
    "passing_score": skill["passing_score"],
    "status": status,
    "date": datetime.now().isoformat(timespec="seconds"),
    "concept_results": concept_results,
    "weak_concepts": weak_concepts
}


# ==========================================
# 6A. LEARNING GAP REPORT
# ==========================================

print("\n" + "=" * 45)
print("            LEARNING GAP REPORT")
print("=" * 45)

print(f"Skill: {skill['name']}")
print(f"Score: {score}/{total_questions}")
print(f"Percentage: {percentage:.1f}%")
print(f"Required score: {skill['passing_score']}%")
print(f"Status: {status}")


# ==========================================
# 6B. CONCEPT-WISE PERFORMANCE
# ==========================================

print("\n" + "=" * 45)
print("      CONCEPT-WISE PERFORMANCE")
print("=" * 45)

for concept, result in concept_results.items():
    attempted = result["attempted"]
    correct = result["correct"]
    concept_percentage = (correct / attempted) * 100

    print(f"\nConcept: {concept.replace('_', ' ').title()}")
    print(f"Score: {correct}/{attempted}")
    print(f"Accuracy: {concept_percentage:.1f}%")

    if concept in weak_concepts:
        print("Recommendation: Needs more practice")
    else:
        print("Recommendation: Keep practising to maintain progress")

if weak_concepts:
    print("\nYour personalised learning plan:")

    for concept in weak_concepts:
        resource = learning_resources.get(concept)
        print(f"\n{concept.replace('_', ' ').title()}")

        if resource:
            print(f"  Topic: {resource['topic']}")
            print(f"  Study: {resource['action']}")
            print(f"  Practice: {resource['practice']}")
        else:
            print("  Study: Review this concept and practise related questions.")


# ==========================================
# 7. RECOMMEND NEXT STEPS
# ==========================================

dependent_skills = []

for other_skill_id, details in skill_tree.items():
    if skill_id in details["prerequisites"]:
        dependent_skills.append(details["name"])

print("\n" + "=" * 45)
print("         RECOMMENDED NEXT STEPS")
print("=" * 45)

if not passed:
    print(f"Focus on improving {skill['name']} first.")
    print("Review the relevant concepts and practise before retaking.")

    if weak_concepts:
        print("\nPrioritise these concepts:")
        for concept in weak_concepts:
            print(f"- {concept.replace('_', ' ').title()}")

    if dependent_skills:
        print("\nSkills that build on this prerequisite:")
        for name in dependent_skills:
            print(f"- {name}")

else:
    print("You have met the passing threshold.")
    print("You can proceed to the next learning stage.")

    if dependent_skills:
        print("\nSkills that build on this foundation:")
        for name in dependent_skills:
            print(f"- {name}")


# ==========================================
# 8. LOAD EXISTING HISTORY
# ==========================================

try:
    with open(file_name, "r", encoding="utf-8") as file:
        results = json.load(file)

    if not isinstance(results, list):
        raise ValueError(
            f"{file_name} must contain a JSON list of assessment records."
        )

except FileNotFoundError:
    results = []

except json.JSONDecodeError as error:
    raise ValueError(
        f"{file_name} contains invalid JSON. "
        "Repair the file before running another assessment."
    ) from error


# ==========================================
# 9. CLEAN OLD RECORDS
# ==========================================

summary_fields = [
    "skill_id",
    "skill_name",
    "score",
    "total_questions",
    "percentage",
    "passing_score",
    "status",
    "date",
    "concept_results",
    "weak_concepts"
]

cleaned_results = []

for result in results:
    if not isinstance(result, dict):
        continue

    cleaned_result = {
        key: result[key]
        for key in summary_fields
        if key in result
    }

    if cleaned_result:
        cleaned_results.append(cleaned_result)

previous_attempts = [
    result
    for result in cleaned_results
    if result.get("skill_id") == skill_id
]

cleaned_results.append(assessment_result)

# ==========================================
# 10. PERSONALIZED LEARNING-PATH GENERATOR
# ==========================================

print("\n" + "=" * 45)
print("       MASTER PERSONALIZED LEARNING ROADMAP")
print("=" * 45)

# Aggregate all weak concepts across all recorded history for this user
cumulative_weak_concepts = set()
passed_skills_set = set()

for res in cleaned_results:
    if res.get("status") == "Demonstrated":
        passed_skills_set.add(res.get("skill_id"))
    for wc in res.get("weak_concepts", []):
        cumulative_weak_concepts.add(wc)

print("\n[Phase 1: Targeted Remediation]")
if cumulative_weak_concepts:
    print("You have cumulative weak concepts to review across your learning history:")
    for concept in sorted(cumulative_weak_concepts):
        resource = learning_resources.get(concept)
        print(f"\n  • Concept: {concept.replace('_', ' ').title()}")
        if resource:
            print(f"    - Topic: {resource['topic']}")
            print(f"    - Action: {resource['action']}")
            print(f"    - Practice: {resource['practice']}")
        else:
            print("    - Action: Review core notes and solve related practice problems.")
else:
    print("  ✓ No unresolved weak concepts! Excellent job keeping your foundation clean.")

print("\n[Phase 2: Milestone Progression]")
unlocked_next_skills = []
for sid, details in skill_tree.items():
    if sid in passed_skills_set:
        continue  # Already mastered
    
    prerequisites = details["prerequisites"]
    if all(p in passed_skills_set for p in prerequisites):
        if sid in question_bank and question_bank[sid]:
            unlocked_next_skills.append(details["name"])

if unlocked_next_skills:
    print("Your next available skill milestones to unlock:")
    for name in unlocked_next_skills:
        print(f"  ➜ {name}")
else:
    print("  ✓ You have unlocked and mastered all currently available skills in the tree!")


# ==========================================
# 11. PROGRESS REPORT
# ==========================================

print("\n" + "=" * 45)
print("             PROGRESS REPORT")
print("=" * 45)

attempt_count = len(previous_attempts) + 1
current_percentage = assessment_result["percentage"]

print(f"Skill: {skill['name']}")
print(f"Total attempts for this skill: {attempt_count}")

if previous_attempts:
    previous_result = previous_attempts[-1]
    previous_percentage = previous_result.get("percentage")

    if isinstance(previous_percentage, (int, float)):
        change = round(
            current_percentage - previous_percentage,
            1
        )

        print(f"Previous score: {previous_percentage:.1f}%")
        print(f"Latest score: {current_percentage:.1f}%")

        if change > 0:
            print(f"Score change: +{change:.1f} percentage points")
            print("Trend: Improving")
        elif change < 0:
            print(f"Score change: {change:.1f} percentage points")
            print("Trend: Declining")
        else:
            print("Score change: 0.0 percentage points")
            print("Trend: Unchanged")
    else:
        print(f"Latest score: {current_percentage:.1f}%")
        print("Previous score is unavailable.")
else:
    print(f"Latest score: {current_percentage:.1f}%")
    print("This is the first recorded attempt for this skill.")


# ==========================================
# 12. CONCEPT PROGRESS COMPARISON
# ==========================================

print("\n" + "=" * 45)
print("      CONCEPT PROGRESS COMPARISON")
print("=" * 45)

if not previous_attempts:
    print("No previous attempt available for comparison.")
    print("Complete another assessment to track concept progress.")
else:
    previous_concepts = previous_attempts[-1].get(
        "concept_results", {}
    )

    compared_concepts = 0

    for concept, current_data in concept_results.items():
        if concept not in previous_concepts:
            continue

        old_data = previous_concepts[concept]

        old_attempted = old_data.get("attempted", 0)
        old_correct = old_data.get("correct", 0)

        current_attempted = current_data["attempted"]
        current_correct = current_data["correct"]

        if old_attempted <= 0 or current_attempted <= 0:
            continue

        old_accuracy = (old_correct / old_attempted) * 100
        current_accuracy = (
            current_correct / current_attempted
        ) * 100

        change = round(current_accuracy - old_accuracy, 1)

        print(f"\nConcept: {concept.replace('_', ' ').title()}")
        print(f"Previous accuracy: {old_accuracy:.1f}%")
        print(f"Current accuracy: {current_accuracy:.1f}%")

        if change > 0:
            print(f"Progress: +{change:.1f} percentage points (Improving)")
        elif change < 0:
            print(f"Progress: {change:.1f} percentage points (Declining)")
        else:
            print("Progress: No change")

        compared_concepts += 1

    if compared_concepts == 0:
        print(
            "No concepts appeared in both attempts. "
            "Run another assessment to collect comparable results."
        )

# ==========================================
# 13. SHOW DASHBOARD
# ==========================================
try:
    show_dashboard(file_name)
except Exception:
    pass

print("\nAssessment completed.")