import sys
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
    st.sidebar.header("Co-Pilot Filters")
    selected_city = st.sidebar.selectbox(
        "City",
        options=all_cities,
        key="copilot_city",
    )
    days_range = st.sidebar.slider(
        "Time range (days)",
        min_value=30,
        max_value=365,
        value=90,
        step=1,
        key="copilot_days",
    )

    filtered = data_loader.filter_reviews(df, selected_city, days_range)
    num_reviews = len(filtered)

    st.subheader(f"AI Manager Co-Pilot — {selected_city}")
    st.caption(
        f"Showing reviews from the last **{days_range} days** · "
        f"**{num_reviews}** matching review{'s' if num_reviews != 1 else ''} found"
    )

    if num_reviews == 0:
        st.warning(
            f"No reviews found for **{selected_city}** in the last {days_range} days. "
            "Try a different city or extend the time range."
        )
    else:
        if st.button("Generate Insights", type="primary"):
            with st.spinner("Analysing reviews with Claude..."):
                result = llm.generate_insights(filtered, selected_city, days_range)
            st.markdown("---")
            st.markdown(result)
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
