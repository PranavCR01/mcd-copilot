import re
import sys
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data_loader
import llm

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="McDonald's Social Media Command Centre",
    page_icon="🍔",
    layout="wide",
)

st.title("🍔 McDonald's Social Media Command Centre")

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

df = data_loader.get_df()
all_cities = sorted(df["city"].dropna().unique().tolist())
all_streets = sorted(df["street"].dropna().unique().tolist())


def _build_health_table(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("street", sort=False)
        .agg(City=("city", "first"), avg_rating=("rating", "mean"), total_reviews=("rating", "count"))
        .reset_index()
        .rename(columns={"street": "Branch", "total_reviews": "Total Reviews"})
    )

    recent = df[df["total_days_ago"] <= 30].groupby("street")["rating"].mean()
    prev = df[(df["total_days_ago"] > 30) & (df["total_days_ago"] <= 60)].groupby("street")["rating"].mean()

    def _trend(street):
        r, p = recent.get(street), prev.get(street)
        if r is None or p is None:
            return "➡️"
        diff = r - p
        return "⬆️" if diff > 0.1 else "⬇️" if diff < -0.1 else "➡️"

    def _status(avg):
        if avg < 2.5:
            return "🔴 Needs Attention"
        if avg <= 3.5:
            return "🟡 Monitor"
        return "🟢 Healthy"

    summary["Avg Rating"] = summary["avg_rating"].round(2)
    summary["Status"] = summary["avg_rating"].apply(_status)
    summary["Trend"] = summary["Branch"].apply(_trend)

    return (
        summary[["Branch", "City", "Avg Rating", "Total Reviews", "Status", "Trend"]]
        .sort_values("Avg Rating")
        .reset_index(drop=True)
    )

def _extract_briefing(result: str) -> str:
    """Return the text under the STAFF BRIEFING header, or empty string if not found."""
    idx = result.upper().find("STAFF BRIEFING")
    if idx == -1:
        return ""
    after_header = result[idx + len("STAFF BRIEFING"):]
    return after_header.strip()


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab1, tab2 = st.tabs(["Review Dashboard", "AI Manager Co-Pilot"])

# ===========================================================================
# TAB 1 — Review Dashboard
# ===========================================================================

with tab1:
    st.sidebar.header("Dashboard Filters")
    selected_cities = st.sidebar.multiselect(
        "Filter by city",
        options=all_cities,
        default=all_cities,
        key="dashboard_cities",
    )

    dash_df = df[df["city"].isin(selected_cities)] if selected_cities else df

    if dash_df.empty:
        st.warning("No reviews match the selected cities.")
    else:
        st.subheader("Overview")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Reviews", f"{len(dash_df):,}")
        c2.metric("Avg Rating", f"{dash_df['rating'].mean():.2f}")
        c3.metric("Cities", str(dash_df["city"].nunique()))

        st.divider()

        # Row 1: rating distribution + review length boxplot
        row1_left, row1_right = st.columns(2)

        with row1_left:
            st.subheader("Rating Distribution")
            rating_counts = (
                dash_df["rating"]
                .value_counts()
                .sort_index()
                .reset_index()
            )
            rating_counts.columns = ["rating", "count"]
            fig, ax = plt.subplots(figsize=(5, 3.5))
            ax.bar(
                rating_counts["rating"].astype(str),
                rating_counts["count"],
                color="#DA291C",
                edgecolor="white",
            )
            ax.set_xlabel("Rating")
            ax.set_ylabel("Number of Reviews")
            ax.set_title("Reviews by Star Rating")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        with row1_right:
            st.subheader("Review Length by Rating")
            fig, ax = plt.subplots(figsize=(5, 3.5))
            groups = [
                dash_df.loc[dash_df["rating"] == r, "review_length"].dropna().tolist()
                for r in sorted(dash_df["rating"].unique())
            ]
            labels = [str(r) for r in sorted(dash_df["rating"].unique())]
            ax.boxplot(groups, labels=labels, patch_artist=True,
                       boxprops=dict(facecolor="#FFC72C", color="#DA291C"),
                       medianprops=dict(color="#DA291C", linewidth=2),
                       whiskerprops=dict(color="#333333"),
                       capprops=dict(color="#333333"),
                       flierprops=dict(marker="o", markersize=2, alpha=0.3))
            ax.set_xlabel("Rating")
            ax.set_ylabel("Review Length (chars)")
            ax.set_title("Review Length Distribution per Rating")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        st.divider()

        # Row 2: top 10 cities + correlation heatmap
        row2_left, row2_right = st.columns(2)

        with row2_left:
            st.subheader("Top 10 Cities by Review Count")
            top_cities = (
                dash_df["city"]
                .value_counts()
                .head(10)
                .sort_values(ascending=True)
                .reset_index()
            )
            top_cities.columns = ["city", "count"]
            fig, ax = plt.subplots(figsize=(5, 3.5))
            ax.barh(top_cities["city"], top_cities["count"],
                    color="#DA291C", edgecolor="white")
            ax.set_xlabel("Number of Reviews")
            ax.set_title("Top 10 Cities")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        with row2_right:
            st.subheader("Correlation Heatmap")
            corr_cols = ["rating", "rating_count", "review_length", "total_days_ago"]
            available = [c for c in corr_cols if c in dash_df.columns]
            corr = dash_df[available].corr()
            fig, ax = plt.subplots(figsize=(5, 3.5))
            sns.heatmap(
                corr,
                annot=True,
                fmt=".2f",
                cmap="RdYlGn",
                linewidths=0.5,
                ax=ax,
                vmin=-1,
                vmax=1,
            )
            ax.set_title("Feature Correlations")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

# ===========================================================================
# TAB 2 — AI Manager Co-Pilot
# ===========================================================================

with tab2:
    # -----------------------------------------------------------------------
    # Branch Health Overview
    # The table must render (and row-click detection must run) BEFORE the
    # sidebar selectbox, so that session_state["copilot_branch"] is updated
    # in time for the selectbox to reflect the clicked branch.
    # -----------------------------------------------------------------------
    st.subheader("Branch Health Overview")
    st.caption("Click any row to load that branch in the Co-Pilot below.")

    health_df = _build_health_table(df)
    health_event = st.dataframe(
        health_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
    )

    if health_event.selection.rows:
        clicked_street = health_df.iloc[health_event.selection.rows[0]]["Branch"]
        st.session_state["copilot_branch"] = clicked_street

    st.divider()

    # -----------------------------------------------------------------------
    # Co-Pilot Filters (sidebar)
    # -----------------------------------------------------------------------
    st.sidebar.header("Co-Pilot Filters")
    selected_branch = st.sidebar.selectbox(
        "Branch",
        options=all_streets,
        key="copilot_branch",
    )
    days_range = st.sidebar.slider(
        "Time range (days)",
        min_value=30,
        max_value=365,
        value=90,
        step=1,
        key="copilot_days",
    )

    filtered = data_loader.filter_reviews(df, selected_branch, days_range)
    num_reviews = len(filtered)

    st.subheader(f"AI Manager Co-Pilot — {selected_branch}")
    st.caption(
        f"Showing reviews from the last **{days_range} days** · "
        f"**{num_reviews}** matching review{'s' if num_reviews != 1 else ''} found"
    )

    if num_reviews == 0:
        st.warning(
            f"No reviews found for **{selected_branch}** in the last {days_range} days. "
            "Try a different branch or extend the time range."
        )
    else:
        if st.button("Generate Insights", type="primary"):
            with st.spinner("Analysing reviews with Claude..."):
                result = llm.generate_insights(filtered, selected_branch, days_range)
            st.markdown("---")
            st.markdown(result)

            briefing_text = _extract_briefing(result)
            if briefing_text:
                st.divider()
                st.subheader("Staff Briefing")
                st.code(briefing_text, language=None)

                safe_name = re.sub(r"[^\w\-]", "_", selected_branch)
                filename = f"briefing_{safe_name}_{date.today()}.txt"
                st.download_button(
                    label="Download Staff Briefing (.txt)",
                    data=briefing_text,
                    file_name=filename,
                    mime="text/plain",
                )

            st.divider()

        st.subheader("Reviews Used")
        display_cols = [c for c in ["rating", "review", "total_days_ago", "review_length"]
                        if c in filtered.columns]
        preview = (
            filtered[display_cols]
            .sort_values("total_days_ago", ascending=True)
            .head(50)
            .reset_index(drop=True)
        )
        preview.index += 1
        st.dataframe(preview, use_container_width=True)
