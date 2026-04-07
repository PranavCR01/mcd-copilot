# Safety & Privacy

## PII Handling

Customer reviews from the Kaggle dataset are public submissions and do not contain directly identifying information (no names, emails, or account IDs are present in the dataset columns used).

Before reviews are sent to the Claude API:
- Only the `review` text and `rating` value are included — no store addresses, coordinates, or reviewer metadata.
- Non-ASCII characters are stripped at load time to remove encoding artefacts.
- Reviews are sent as plain text strings with no additional user context or session state.

The app does not collect, store, or transmit any information about the person using the app.

## Rate Limits and Token Caps

A hard cap of **20 reviews per API call** is enforced in `llm.py` before constructing the prompt. This:
- Keeps prompt size within a predictable token budget.
- Prevents accidental large payloads if a branch has hundreds of recent reviews.
- Ensures response latency stays acceptable for interactive use.

## Jailbreak Mitigations

The system prompt in `prompts/manager_copilot.txt` explicitly instructs the model to:
- Base all output strictly on the review text provided.
- Not speculate beyond what the reviews contain.
- Respond only in the three structured sections: `SUMMARY`, `ACTION ITEMS`, `STAFF BRIEFING`.

This grounding constraint limits the model's ability to generate off-topic, harmful, or fabricated content, since it is instructed to treat the reviews as the sole evidence base.

User input does not flow into the system prompt. The only user-controlled variable is the branch name and time range, which are used to filter the dataset — not injected into the prompt string.

## Data Storage

The app stores **only LLM call logs** in `llm_logs.db` (SQLite, project root). Logged fields are: timestamp, branch name, days range, number of reviews sent, and the full response text. No review text sent to the API is stored separately.

`llm_logs.db` is a local file and is not transmitted anywhere. It is excluded from version control via `.gitignore`.
