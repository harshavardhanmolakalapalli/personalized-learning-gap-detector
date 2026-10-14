
skill_tree = {
    "python_basics": {
        "name": "Python Fundamentals",
        "level": 1,
        "prerequisites": [],
        "passing_score": 80,
        "assessment": "Score 8/10 and complete 2 coding tasks"
    },
    "data_structures": {
        "name": "Python Data Structures",
        "level": 1,
        "prerequisites": ["python_basics"],
        "passing_score": 80,
        "assessment": "Solve 4 out of 5 practical problems"
    },
    "functions_debugging": {
        "name": "Functions and Debugging",
        "level": 1,
        "prerequisites": ["python_basics"],
        "passing_score": 80,
        "assessment": "Pass 4 out of 5 function-based tasks"
    },
    "data_handling": {
        "name": "Data Handling with Pandas",
        "level": 2,
        "prerequisites": [
            "python_basics",
            "data_structures"
        ],
        "passing_score": 80,
        "assessment": "Complete 4 out of 5 data manipulation tasks"
    },
    "statistics": {
        "name": "Statistics and Probability",
        "level": 2,
        "prerequisites": ["python_basics"],
        "passing_score": 80,
        "assessment": "Solve 8 out of 10 foundational problems"
    },
    "machine_learning": {
        "name": "Machine Learning Fundamentals",
        "level": 3,
        "prerequisites": [
            "data_handling",
            "statistics"
        ],
        "passing_score": 80,
        "assessment": "Build and evaluate a baseline ML model"
    }
}
# Display skills only when this file runs directly
if __name__ == "__main__":
    for skill_id, details in skill_tree.items():
        print(f"\nSkill: {details['name']}")
        print(f"Level: {details['level']}")
        print(f"Prerequisites: {details['prerequisites']}")
        print(f"Passing score: {details['passing_score']}%")
        print(f"Assessment: {details['assessment']}")
        print("-" * 40)