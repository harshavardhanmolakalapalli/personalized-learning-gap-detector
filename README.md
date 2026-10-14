Hey, I'm Harsha Vardhan 👋

Aspiring AI Engineer | Python Developer | AI & Machine Learning Enthusiast

I'm a Computer Science graduate focused on building practical software projects and developing my skills in Python, Artificial Intelligence, and Machine Learning.

I enjoy learning by building projects, experimenting with AI tools, and solving problems through code.

🚀 Featured Project

🧠 Personalized Learning Gap Detector

A Python-based learning assessment application that identifies concepts a learner may need to practise and suggests appropriate next steps.

Features

Skill-based multiple-choice assessments

Per-concept performance tracking and weak-concept detection

Personalized learning recommendations and practice activities

Prerequisite-aware learning paths using a skill tree

Local assessment history and progress dashboard

Optional AI-generated practice questions using Google's Gemini API

Unit tests for question-bank structure, skill prerequisites, and AI response validation

Tech Stack

Python · Streamlit · Pandas · Google Gen AI SDK

🔗 Repository: Personalized Learning Gap Detector

🛠️ Skills & Tools

Programming: Python

Frameworks: Streamlit

AI Integration: Google Gemini API

Data Handling: Pandas, JSON

Developer Tools: Git, GitHub, VS Code

📚 Currently Learning

Python programming and problem-solving

Data structures and algorithms

Mathematics and statistics for Machine Learning

Machine Learning fundamentals

AI application development

🎯 Goals

Build practical AI and Machine Learning projects

Strengthen my programming and problem-solving skills

Develop a strong AI engineering portfolio

Contribute to open-source projects

Keep learning by building real-world applications

🤝 Let's Connect

I'm interested in Artificial Intelligence, Machine Learning, Python development, and building technology that solves practical problems.

Thanks for visiting my profile! 🚀
# Personalized Learning Gap Detector

A Python learning-assessment project that identifies concepts a learner may need to practise and suggests next steps. It includes a Streamlit interface, a prerequisite-based skill tree, a question bank, assessment history, and optional Gemini-powered practice-question generation.

## Features

- Skill-based multiple-choice assessments
- Per-concept performance tracking and weak-concept detection
- Learning recommendations and practice activities
- Prerequisite-aware learning path
- Local assessment history and progress dashboard
- Optional AI-generated practice questions using Google's Gemini API
- Unit tests for question-bank structure, skill prerequisites, and AI response validation

## Tech stack

- Python
- Streamlit
- Pandas
- Google Gen AI SDK

## Project structure

```text
personalized-learning-gap-detector/
├── app.py
├── ai_generator.py
├── assignment.py
├── dashboard.py
├── main.py
├── question_bank.py
├── recommendation.py
├── skill_tree.py
├── test.py
├── test_ai_generator.py
├── requirements.txt
├── .gitignore
├── README.md
├── .streamlit/
│   └── secrets.toml.example
└── screenshots/
```

## Run locally

### 1. Create a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Gemini (optional AI feature)

Create `.streamlit/secrets.toml` with your own API key:

```toml
GEMINI_API_KEY = "your-own-gemini-api-key"
```

The real `secrets.toml` is ignored by Git. Never paste API keys into source code or commit them to GitHub. If a key was exposed publicly, revoke it and generate a replacement.

### 4. Start the Streamlit app

```powershell
streamlit run app.py
```

The terminal will show the local URL, usually `http://localhost:8501`.

The repository also includes a command-line entry point:

```powershell
python main.py
```

## Run tests

```powershell
python -m unittest -v test.py test_ai_generator.py
```

The AI generator tests mock the Gemini response, so they do not intentionally make a live API request. A real generated question still requires a valid key, internet access, and model availability.

## Data and privacy

Assessment history is stored locally in `assessment_results.json`. The file is intentionally excluded from Git because it may contain personal learning history. The app can create a new local history file when you run assessments.

## Screenshots

Add screenshots of the running app under `screenshots/`. Use fictional/demo data and ensure no API keys or private learner records are visible.

## Roadmap

- Expand the question bank and review question quality
- Continue improving learning-resource coverage
- Add more tests for scoring, question selection, and recommendations
- Improve handling of temporary Gemini API errors
- Add screenshots and a short demo

## License

No license is included yet. Choose a license before inviting others to reuse or redistribute the project.
