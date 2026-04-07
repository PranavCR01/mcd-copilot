# Installation Guide

## Prerequisites

- Python 3.9 or higher
- A Kaggle account (the dataset is downloaded automatically via `kagglehub`)
- An Anthropic API key

## Setup

**1. Clone the repository**

```bash
git clone <repo-url>
cd mcdo-copilot
```

**2. Create your environment file**

Copy the example and add your API key:

```bash
cp .env.example .env
```

Open `.env` and set:

```
ANTHROPIC_API_KEY=sk-ant-...
```

**3. Install dependencies**

```bash
python -m pip install -r requirements.txt
```

**4. Run the app**

Always run from the project root (`mcdo-copilot/`), not from inside `app/`:

```bash
python -m streamlit run app/app.py
```

The app will open in your browser at `http://localhost:8501`.

## Notes

- The Kaggle dataset is downloaded automatically on first run via `kagglehub` and cached locally.
- The SQLite log file `llm_logs.db` is created in the project root on the first AI Co-Pilot call.
- If you see a database error mentioning a missing column, delete `llm_logs.db` and restart — the schema will be recreated.
