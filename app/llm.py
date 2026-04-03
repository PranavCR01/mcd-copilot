import sqlite3
import textwrap
from datetime import datetime
from pathlib import Path

import os

import anthropic
import pandas as pd
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_ROOT = Path(__file__).resolve().parent.parent
_PROMPT_FILE = _ROOT / "prompts" / "manager_copilot.txt"
_DB_FILE = _ROOT / "llm_logs.db"

_MODEL = "claude-haiku-4-5-20251001"
_MAX_TOKENS = 1000

# ---------------------------------------------------------------------------
# DB setup
# ---------------------------------------------------------------------------

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_FILE)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS llm_logs (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp     TEXT    NOT NULL,
            branch        TEXT    NOT NULL,
            days_range    INTEGER NOT NULL,
            num_reviews   INTEGER NOT NULL,
            response_text TEXT    NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def _log(branch: str, days_range: int, num_reviews: int, response_text: str) -> None:
    conn = _get_conn()
    conn.execute(
        "INSERT INTO llm_logs (timestamp, branch, days_range, num_reviews, response_text) "
        "VALUES (?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), branch, days_range, num_reviews, response_text),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Prompt helpers
# ---------------------------------------------------------------------------

def _load_system_prompt() -> str:
    return _PROMPT_FILE.read_text(encoding="utf-8")


def _format_reviews(df: pd.DataFrame) -> str:
    top = (
        df.sort_values("total_days_ago", ascending=True)
        .head(20)
        .reset_index(drop=True)
    )
    lines = [
        f"{i + 1}. [{row['rating']}/5] {row['review']}"
        for i, row in top.iterrows()
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_insights(reviews_df: pd.DataFrame, branch: str, days_range: int) -> str:
    """
    Call the Claude API and return the structured analysis.

    Parameters
    ----------
    reviews_df : DataFrame already filtered to the target branch / date window.
    branch     : Human-readable branch address (used for logging only).
    days_range : Day window used to filter reviews (used for logging only).

    Returns
    -------
    str  — The model's response text, or an error message.
    """
    if reviews_df.empty:
        return "No reviews found for the selected branch and time range."

    system_prompt = _load_system_prompt()
    formatted = _format_reviews(reviews_df)
    user_message = (
        f"Here are the most recent customer reviews for the {branch} branch:\n\n"
        f"{formatted}"
    )

    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model=_MODEL,
            max_tokens=_MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
    except anthropic.AuthenticationError:
        return "Authentication failed. Check that ANTHROPIC_API_KEY is set in your .env file."
    except anthropic.APIConnectionError:
        return "Could not reach the Anthropic API. Check your internet connection."
    except anthropic.APIStatusError as exc:
        return f"Anthropic API error: {exc.status_code} {exc.message}"

    response_text = message.content[0].text.strip()

    if not response_text:
        return "The model returned an empty response. Please try again."

    _log(
        branch=branch,
        days_range=days_range,
        num_reviews=min(len(reviews_df), 20),
        response_text=response_text,
    )

    return response_text
