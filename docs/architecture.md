# Architecture

```
User (browser) → Streamlit app (app.py)
  ├── Tab 1: Review Dashboard → data_loader.py → Kaggle CSV dataset
  └── Tab 2: AI Co-Pilot → llm.py → Claude API (claude-haiku-4-5-20251001)
                                  → SQLite (llm_logs.db) for telemetry
```

## Components

- **data_loader.py** — loads, cleans, and caches the Kaggle dataset using `@st.cache_data`
- **llm.py** — filters top 20 reviews, builds prompt, calls Claude API, logs to SQLite
- **prompts/manager_copilot.txt** — system prompt grounding the LLM in review text only
- **llm_logs.db** — logs every API call with `timestamp`, `branch`, `days_range`, `num_reviews`, `response_text`
