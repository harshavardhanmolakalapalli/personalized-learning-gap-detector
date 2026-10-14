
import json
import os

FILE_NAME = "assessment_results.json"


def load_results():
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            results = json.load(file)

        if not isinstance(results, list):
            print("Error: Assessment history must be a JSON list.")
            return []

        return results

    except FileNotFoundError:
        print("No assessment history found.")
        print("Run assignment.py first.")
        return []

    except json.JSONDecodeError:
        print("Assessment history contains invalid JSON.")
        return []


def show_dashboard():
    results = load_results()

    if not results:
        return

    valid_results = [
        result for result in results
        if isinstance(result, dict)
        and isinstance(result.get("percentage"), (int, float))
    ]

    if not valid_results:
        print("No valid assessment results found.")
        return

    # Sort by recorded date, with file order as a fallback.
    dated_results = [
        (index, result)
        for index, result in enumerate(valid_results)
        if isinstance(result.get("date"), str)
    ]

    if dated_results:
        latest = max(dated_results, key=lambda item: (item[1]["date"], item[0]))[1]
    else:
        latest = valid_results[-1]

    skill_id = latest.get("skill_id")
    skill_results = [
        result for result in valid_results
        if result.get("skill_id") == skill_id
    ]

    print("\n" + "=" * 45)
    print("       LEARNING PROGRESS DASHBOARD")
    print("=" * 45)

    print(f"Skill: {latest.get('skill_name', 'Unknown')}")
    print(f"Total attempts: {len(skill_results)}")
    print(f"Latest score: {latest['percentage']:.1f}%")
    print(f"Status: {latest.get('status', 'Unknown')}")

    if len(skill_results) >= 2:
        previous = skill_results[-2]
        change = round(
            latest["percentage"] - previous["percentage"], 1
        )

        print(f"Previous score: {previous['percentage']:.1f}%")
        print(f"Score change: {change:+.1f} percentage points")

    print("\nLATEST CONCEPT PERFORMANCE")
    print("-" * 45)

    concept_results = latest.get("concept_results", {})

    if not concept_results:
        print("No concept-level results recorded.")
    else:
        for concept, data in concept_results.items():
            attempted = data.get("attempted", 0)
            correct = data.get("correct", 0)

            if attempted <= 0:
                continue

            accuracy = (correct / attempted) * 100

            print(
                f"{concept.replace('_', ' ').title()}: "
                f"{correct}/{attempted} ({accuracy:.1f}%)"
            )

    print("\nCONCEPTS TO PRACTISE")
    print("-" * 45)

    weak_concepts = latest.get("weak_concepts", [])

    if weak_concepts:
        for concept in weak_concepts:
            print(f"- {concept.replace('_', ' ').title()}")
    else:
        print("No weak concepts were recorded in this attempt.")

    print("\n" + "=" * 45)
    print("Dashboard completed.")


if __name__ == "__main__":
    show_dashboard()
