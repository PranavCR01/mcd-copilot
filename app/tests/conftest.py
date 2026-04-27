import sys
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Stub heavy dependencies BEFORE any project module is imported.
# - streamlit.cache_data is replaced with a plain pass-through so get_df()
#   is callable without a running Streamlit server.
# - kagglehub and anthropic are replaced with MagicMocks so no network
#   calls or API keys are required during tests.
# ---------------------------------------------------------------------------

_st_mock = MagicMock()
_st_mock.cache_data = lambda f: f
sys.modules["streamlit"] = _st_mock
sys.modules["kagglehub"] = MagicMock()
sys.modules["anthropic"] = MagicMock()

# Make app/ importable without a package prefix (e.g. `import data_loader`).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Small pre-built DataFrame matching the shape produced by get_df()."""
    return pd.DataFrame(
        {
            "rating": pd.array([5, 4, 1, 3, 5], dtype="Int64"),
            "review": [
                "Great food!",
                "Pretty good",
                "Terrible service",
                "Average at best",
                "Love it here!",
            ],
            "street": [
                "123 Main St",
                "123 Main St",
                "456 Oak Ave",
                "456 Oak Ave",
                "123 Main St",
            ],
            "city": [
                "Springfield",
                "Springfield",
                "Shelbyville",
                "Shelbyville",
                "Springfield",
            ],
            "total_days_ago": [10.0, 20.0, 50.0, 100.0, 5.0],
            "review_length": [11, 11, 16, 15, 13],
            "zip": ["62701", "62701", "62702", "62702", "62701"],
            "country": ["United States"] * 5,
            "rating_count": [100, 100, 50, 50, 100],
            "years_ago": [0, 0, 0, 0, 0],
            "months_ago": [0, 1, 2, 3, 0],
            "days_ago": [10, 20, 50, 100, 5],
            "hours_ago": [0, 0, 0, 0, 0],
        }
    )
