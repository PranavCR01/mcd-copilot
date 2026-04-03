# McDonald's Social Media Command Centre

## Project Overview

IS492 GenAI course project. Analyzes McDonald's customer reviews using the Anthropic Claude API.

**Dataset:** [nelgiriyewithana/mcdonalds-store-reviews](https://www.kaggle.com/datasets/nelgiriyewithana/mcdonalds-store-reviews) (Kaggle)

The app has two tabs:
- **Review Dashboard** — filters and visualizes customer reviews by city
- **AI Manager Co-Pilot** — branch health overview table, then filtered reviews sent to Claude for actionable insights with a downloadable staff briefing

---

## File Structure

```
mcdo-copilot/
├── app/
│   ├── app.py              # Main Streamlit app, defines both tabs
│   ├── data_loader.py      # Loads and cleans Kaggle dataset; exposes get_df() and filter_reviews()
│   └── llm.py              # Calls Anthropic Claude API, logs to SQLite; exposes generate_insights()
├── prompts/
│   └── manager_copilot.txt # System prompt: outputs SUMMARY / ACTION ITEMS / STAFF BRIEFING
├── docs/                   # Architecture diagrams and use cases
├── requirements.txt
└── .env.example
```

---

## Environment Setup

1. Copy `.env.example` to `.env` in the **project root** (`mcdo-copilot/`).
2. Add your key:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app from the **project root**:
   ```bash
   python -m streamlit run app/app.py
   ```

---

## Key Technical Decisions

- **Rating column parsing:** The `rating` column contains strings like `"1 star"` or `"5 stars"`, not integers. `data_loader.py` extracts the numeric value with regex before any filtering or aggregation.
- **dotenv path:** `llm.py` loads `.env` using an explicit path — `parent.parent` of `llm.py` — to ensure it always resolves to the project root regardless of the working directory.
- **Review cap:** Only the 20 most recent reviews are sent to the LLM to stay within token limits and keep responses focused.
- **SQLite logging:** Every LLM call is logged to `llm_logs.db` (project root). Schema: `llm_logs(id, timestamp, branch, days_range, num_reviews, response_text)`.
- **Model:** `claude-haiku-4-5-20251001`
- **Branch filter:** `filter_reviews(df, street, days)` in `data_loader.py` filters by exact match on the `street` column (parsed from `store_address`). Tab 1 (Dashboard) still filters by city; Tab 2 (Co-Pilot) filters by street/branch.
- **Branch Health Overview:** Built by `_build_health_table(df)` in `app.py`. Trend compares avg rating of `total_days_ago ≤ 30` vs `31–60` days; ±0.1 threshold for stable (➡️). Status thresholds: 🔴 < 2.5, 🟡 2.5–3.5, 🟢 > 3.5.
- **Row-click → branch selector:** The health table renders and detects row selection *before* the sidebar selectbox is rendered. On click, `st.session_state["copilot_branch"]` is set so the selectbox picks it up on the same rerun. This ordering is load-bearing — do not move the selectbox above the health table.
- **Staff briefing extraction:** `_extract_briefing(result)` finds `"STAFF BRIEFING"` (case-insensitive) and returns everything after it. Since STAFF BRIEFING is the last section in the prompt's output format, no end-marker is needed.
- **Briefing filename sanitization:** Street name is sanitized with `re.sub(r"[^\w\-]", "_", street)` before use in the filename `briefing_{street}_{YYYY-MM-DD}.txt`.

---

## Common Gotchas

- Always run from the `mcdo-copilot/` root directory, not from inside `app/`.
- Use `python -m streamlit run app/app.py` — plain `streamlit` command may not work depending on your Python environment.
- `.env` must be in the project root (`mcdo-copilot/.env`), not inside `app/`.
- If `llm_logs.db` already exists from before the `city` → `branch` column rename, delete it — SQLite's `CREATE TABLE IF NOT EXISTS` won't alter an existing table, and the INSERT will fail.

---

## Pending Work (for teammates)

- [x] Switch Co-Pilot filter from city level to branch/street level for more granular analysis
- [x] Add branch overview table with color-coded health status (red/yellow/green) based on rating thresholds
- [x] Add copy/export button for the staff briefing output from Co-Pilot
- [ ] UI polish — McDonald's branding (red/yellow palette), better layout and typography
