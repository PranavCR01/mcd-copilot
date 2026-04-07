# 🍟 McDonald's Social Media Command Centre

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B?logo=streamlit&logoColor=white)
![Claude](https://img.shields.io/badge/Anthropic-Claude%20Haiku-blueviolet?logo=anthropic&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

> **IS492 — Generative AI for Human-AI Collaboration**
> University of Illinois Urbana-Champaign

---

## Live Demo

**[https://mcd-command-centre.streamlit.app](https://mcd-command-centre.streamlit.app)**

---

## 📋 Project Overview

McDonald's branch managers receive hundreds of customer reviews across social media and review platforms every week, but lack a fast, structured way to extract actionable intelligence from that feedback.

**McDonald's Social Media Command Centre** solves this by combining an interactive analytics dashboard with an AI-powered co-pilot that reads real customer reviews and produces ready-to-use management briefs — so managers can act on feedback, not just read it.

---

## ✨ Features

### 📊 Review Dashboard

An interactive analytics layer built on real customer review data, giving managers a visual pulse on branch performance:

| Chart | What it shows |
|---|---|
| **Rating Distribution** | Breakdown of 1–5 star ratings across locations |
| **Review Length Analysis** | Whether longer reviews skew positive or negative |
| **City Comparisons** | Side-by-side average ratings across branches |
| **Correlation Heatmap** | Statistical relationships between review attributes |

Filter by **city** and **time window** to drill into exactly the reviews that matter.

---

### 🤖 AI Manager Co-Pilot

Powered by **Anthropic Claude**, the Co-Pilot reads up to 20 of the most recent filtered reviews and generates a structured management brief in three sections:

- **SUMMARY** — Overall sentiment and key themes from the reviews
- **ACTION ITEMS** — Concrete, prioritised steps for the manager to take
- **STAFF BRIEFING** — A ready-to-share update for the front-line team

All AI interactions are logged to a local SQLite database for auditability.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | [Streamlit](https://streamlit.io) |
| Data processing | [Pandas](https://pandas.pydata.org) |
| AI model | [Anthropic Claude](https://www.anthropic.com) — `claude-haiku-4-5-20251001` |
| AI logging | SQLite (`llm_logs.db`) |
| Dataset | [Kaggle — nelgiriyewithana/mcdonalds-store-reviews](https://www.kaggle.com/datasets/nelgiriyewithana/mcdonalds-store-reviews) |
| Visualisation | Matplotlib, Seaborn |
| Language | Python 3.10+ |

---

## 🚀 Setup Instructions

### 1. Clone the repository

```bash
git clone <repo-url>
cd mcdo-copilot
```

### 2. Create your `.env` file

Create a `.env` file in the project root with your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

> Get your API key at [console.anthropic.com](https://console.anthropic.com).

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app/app.py
```

The app will open in your browser at `http://localhost:8501`.

> **Note on the dataset:** The McDonald's review dataset is downloaded automatically from Kaggle on first run via the `kagglehub` library. This requires valid Kaggle credentials configured on your machine (`~/.kaggle/kaggle.json`). See the [Kaggle API docs](https://www.kaggle.com/docs/api) for setup instructions.

---

## 📁 Project Structure

```
mcdo-copilot/
├── app/
│   ├── app.py              # Streamlit UI, two tabs, charts, Co-Pilot
│   ├── data_loader.py      # Kaggle dataset download, cleaning, caching
│   └── llm.py              # Anthropic Claude API integration, SQLite logging
├── prompts/
│   └── manager_copilot.txt # System prompt for AI Co-Pilot
├── docs/
│   ├── architecture.md     # System architecture description
│   ├── use-cases.md        # Use case documentation
│   ├── SAFETY.md           # Safety and privacy notes
│   └── TELEMETRY.md        # LLM call logging and observability
├── .env.example            # API key template
├── .gitignore
├── CLAUDE.md               # Context for AI-assisted development
├── INSTALL.md              # Setup and run instructions
├── requirements.txt
└── README.md
```

---

## 👥 Team

| Name | Role |
|---|---|
| Pranav C | AI integration, backend architecture, data pipeline, visualizations, streamlit deployment |
| Jeet T | — |
| Ashish G | — |

**Course:** IS492 — Generative AI for Human-AI Collaboration
**Institution:** University of Illinois Urbana-Champaign

---

## ⚠️ Responsible Use

This tool is intended to assist managers in synthesising customer feedback — not to replace human judgement. All AI-generated content should be reviewed before being acted upon or shared with staff. See [`docs/SAFETY.md`](docs/SAFETY.md) for full responsible use guidelines.
