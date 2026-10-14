
import importlib
import sys

from dashboard import show_dashboard


def main():
    assessment_module = None

    while True:
        print("\n" + "=" * 50)
        print("      PERSONALIZED LEARNING PLATFORM")
        print("=" * 50)
        print("1. Start a New Skill Assessment")
        print("2. View Learner Progress Dashboard")
        print("3. Exit")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == "1":
            print("\nLaunching assessment engine...")

            try:
                if assessment_module is None:
                    assessment_module = importlib.import_module(
                        "assignment"
                    )
                else:
                    importlib.reload(assessment_module)

            except Exception as error:
                print(f"\nAssessment error: {error}")

        elif choice == "2":
            show_dashboard()

        elif choice == "3":
            print("\nGoodbye! Keep learning and building your skills.")
            sys.exit(0)

        else:
            print("\nInvalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
