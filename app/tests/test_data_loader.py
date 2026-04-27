import kagglehub
import pandas as pd
import pytest

import data_loader

# ---------------------------------------------------------------------------
# filter_reviews tests
# ---------------------------------------------------------------------------

def test_filter_reviews_by_city(sample_df):
    """filter_reviews returns only rows whose street matches the given branch.

    '123 Main St' is Springfield; '456 Oak Ave' is Shelbyville.
    Asking for '123 Main St' must exclude all Shelbyville rows.
    """
    result = data_loader.filter_reviews(sample_df, "123 Main St", days=365)

    assert list(result["street"].unique()) == ["123 Main St"]
    assert len(result) == 3


def test_filter_reviews_by_days(sample_df):
    """filter_reviews excludes rows older than the days cutoff.

    '456 Oak Ave' has total_days_ago values of 50 and 100.
    With days=60 only the 50-day-old review should be returned.
    """
    result = data_loader.filter_reviews(sample_df, "456 Oak Ave", days=60)

    assert len(result) == 1
    assert all(result["total_days_ago"] <= 60)


def test_filter_reviews_empty(sample_df):
    """filter_reviews returns an empty DataFrame when no rows match."""
    result = data_loader.filter_reviews(sample_df, "999 Nonexistent Blvd", days=365)

    assert result.empty


# ---------------------------------------------------------------------------
# get_df() transformation tests
# ---------------------------------------------------------------------------

def _write_test_csv(path, rows: list[str]) -> None:
    """Write a minimal reviews CSV to *path* for get_df() to consume."""
    header = (
        "rating,review,store_address,"
        "rating_count,years_ago,months_ago,days_ago,hours_ago\n"
    )
    path.write_text(header + "\n".join(rows) + "\n", encoding="latin-1")


def test_rating_is_numeric(tmp_path, monkeypatch):
    """get_df() converts 'X star(s)' strings to a nullable integer (Int64) column."""
    _write_test_csv(
        tmp_path / "reviews.csv",
        [
            '1 star,Bad food,"123 Main St, Springfield, IL 62701, United States",10,0,0,5,0',
            '4 stars,Good food,"456 Oak Ave, Shelbyville, IL 62702, United States",20,0,1,15,0',
        ],
    )
    monkeypatch.setattr(kagglehub, "dataset_download", lambda _: str(tmp_path))

    df = data_loader.get_df()

    assert pd.api.types.is_integer_dtype(df["rating"]), (
        f"Expected integer dtype, got {df['rating'].dtype}"
    )


def test_review_length_added(tmp_path, monkeypatch):
    """get_df() adds a review_length column with the character count as an integer."""
    review_text = "Hello world"
    _write_test_csv(
        tmp_path / "reviews.csv",
        [
            f'3 stars,{review_text},"789 Elm St, Capital City, IL 62703, United States",5,0,0,3,0',
        ],
    )
    monkeypatch.setattr(kagglehub, "dataset_download", lambda _: str(tmp_path))

    df = data_loader.get_df()

    assert "review_length" in df.columns
    assert pd.api.types.is_integer_dtype(df["review_length"])
    assert df["review_length"].iloc[0] == len(review_text)
