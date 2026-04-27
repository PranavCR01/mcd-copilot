import sqlite3

import pytest

import llm

# ---------------------------------------------------------------------------
# _extract_briefing
# ---------------------------------------------------------------------------

def test_extract_briefing_found():
    """_extract_briefing returns the text that follows the STAFF BRIEFING header."""
    text = (
        "SUMMARY\n"
        "Some summary text.\n\n"
        "ACTION ITEMS\n"
        "1. Fix the fryer.\n\n"
        "STAFF BRIEFING\n"
        "Attention team: please review cleanliness standards."
    )

    result = llm._extract_briefing(text)

    assert result == "Attention team: please review cleanliness standards."


def test_extract_briefing_case_insensitive():
    """Header match is case-insensitive (prompt output may vary in casing)."""
    text = "preamble\n\nstaff briefing\nContent here."

    assert llm._extract_briefing(text) == "Content here."


def test_extract_briefing_missing():
    """_extract_briefing returns an empty string when the header is absent."""
    result = llm._extract_briefing("No briefing section in this text.")

    assert result == ""


# ---------------------------------------------------------------------------
# _get_conn / SQLite logging
# ---------------------------------------------------------------------------

def test_sqlite_log_creates_table(tmp_path, monkeypatch):
    """_get_conn() creates the llm_logs table in the SQLite database."""
    db_path = tmp_path / "test_logs.db"
    monkeypatch.setattr(llm, "_DB_FILE", db_path)

    conn = llm._get_conn()
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='llm_logs'"
    )
    row = cursor.fetchone()
    conn.close()

    assert row is not None, "llm_logs table was not created by _get_conn()"
