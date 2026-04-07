# Telemetry & LLM Call Logs

## Overview

Every call to the Claude API is logged to a local SQLite database (`llm_logs.db`) in the project root. This file is created automatically on the first Co-Pilot run.

## Schema

Table: `llm_logs`

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Auto-incrementing primary key |
| `timestamp` | TEXT | ISO 8601 datetime of the API call (UTC) |
| `branch` | TEXT | Street name of the branch analysed |
| `days_range` | INTEGER | Time window selected by the user (days) |
| `num_reviews` | INTEGER | Number of reviews sent to the model (max 20) |
| `response_text` | TEXT | Full raw response returned by Claude |

## Querying the log

Open the database with the SQLite CLI:

```bash
sqlite3 llm_logs.db
```

**View all calls, most recent first:**

```sql
SELECT id, timestamp, branch, days_range, num_reviews
FROM llm_logs
ORDER BY timestamp DESC;
```

**Find calls for a specific branch:**

```sql
SELECT timestamp, days_range, num_reviews
FROM llm_logs
WHERE branch = '123 Main St'
ORDER BY timestamp DESC;
```

**Count calls per branch:**

```sql
SELECT branch, COUNT(*) AS calls
FROM llm_logs
GROUP BY branch
ORDER BY calls DESC;
```

**Inspect the response for a specific call:**

```sql
SELECT response_text
FROM llm_logs
WHERE id = 5;
```

**Delete all logs (reset):**

```sql
DELETE FROM llm_logs;
```

## Debugging tips

- If the app throws an `OperationalError` about a missing column, the table schema is out of date. Delete `llm_logs.db` from the project root and restart the app — the table will be recreated with the current schema.
- `num_reviews` being lower than expected means the branch had fewer reviews than the 20-review cap within the selected time window.
- A `response_text` that does not contain the expected section headers (`SUMMARY`, `ACTION ITEMS`, `STAFF BRIEFING`) indicates the model deviated from the prompt format — check the system prompt in `prompts/manager_copilot.txt`.
