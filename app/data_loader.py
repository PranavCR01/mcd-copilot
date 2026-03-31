import re
import kagglehub
import pandas as pd
import streamlit as st
from pathlib import Path


@st.cache_data
def get_df() -> pd.DataFrame:
    path = kagglehub.dataset_download("nelgiriyewithana/mcdonalds-store-reviews")
    csv_file = next(Path(path).glob("*.csv"))
    df = pd.read_csv(csv_file, encoding="latin-1")

    # Extract numeric rating from strings like "1 star" / "4 stars"
    df["rating"] = (
        df["rating"].astype(str).str.extract(r"(\d+)")[0].astype("Int64")
    )

    # Drop unused columns
    df = df.drop(columns=["store_name", "category"], errors="ignore")

    # Parse store_address into components
    df = _parse_address(df)

    # Cast rating_count: remove commas, convert to int
    df["rating_count"] = (
        df["rating_count"].astype(str).str.replace(",", "", regex=False)
    )
    df["rating_count"] = pd.to_numeric(df["rating_count"], errors="coerce")

    # Cast review to str
    df["review"] = df["review"].astype(str)

    # Build total_days_ago from component columns
    df["total_days_ago"] = (
        _coerce_numeric(df, "years_ago") * 365
        + _coerce_numeric(df, "months_ago") * 30
        + _coerce_numeric(df, "days_ago")
        + _coerce_numeric(df, "hours_ago") / 24
    )

    # review_length in characters
    df["review_length"] = df["review"].str.len()

    # Drop rows with any nulls
    df = df.dropna()

    df = df.reset_index(drop=True)
    return df


def filter_reviews(df: pd.DataFrame, city: str, days: int) -> pd.DataFrame:
    """Return reviews for *city* posted within the last *days* days."""
    mask = (df["city"].str.lower() == city.lower()) & (df["total_days_ago"] <= days)
    return df[mask].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _coerce_numeric(df: pd.DataFrame, col: str) -> pd.Series:
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce").fillna(0)
    return pd.Series(0, index=df.index)


def _parse_address(df: pd.DataFrame) -> pd.DataFrame:
    """Split store_address (if present) into street / city / zip / country."""
    if "store_address" not in df.columns:
        return df

    parsed = df["store_address"].apply(_split_address)
    df["street"]  = parsed.str[0]
    df["city"]    = parsed.str[1]
    df["zip"]     = parsed.str[2]
    df["country"] = parsed.str[3]
    df = df.drop(columns=["store_address"])
    return df


def _split_address(raw: str):
    """
    Expected US format: '123 Main St, Springfield, IL 62701, United States'
    Returns (street, city, zip, country) — empty string for missing parts.
    """
    if not isinstance(raw, str):
        return ("", "", "", "")

    parts = [p.strip() for p in raw.split(",")]

    street  = parts[0] if len(parts) > 0 else ""
    city    = parts[1] if len(parts) > 1 else ""
    country = parts[-1] if len(parts) > 1 else ""

    # Third segment often contains "STATE ZIP" e.g. "IL 62701"
    state_zip = parts[2] if len(parts) > 2 else ""
    zip_match = re.search(r"\b(\d{5}(?:-\d{4})?)\b", state_zip)
    zip_code  = zip_match.group(1) if zip_match else ""

    return (street, city, zip_code, country)
