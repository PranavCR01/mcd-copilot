import re
import sys
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data_loader
import llm

# ---------------------------------------------------------------------------
# Brand palette
# ---------------------------------------------------------------------------

MCD_RED    = "#DA291C"
MCD_YELLOW = "#FFC72C"
MCD_DARK   = "#1A1A1A"
MCD_CARD   = "#FFFFFF"
MCD_LIGHT  = "#FFF8F0"
MCD_BORDER = "#E8E0D0"
MCD_MUTED  = "#6B6B6B"

# ---------------------------------------------------------------------------
# Page config  (must be first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="McDonald's Command Centre",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS injection
# ---------------------------------------------------------------------------

def _inject_css() -> None:
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Base ─────────────────────────────────────────────────────────── */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    section[data-testid="stMain"] {{
        background: {MCD_LIGHT};
    }}

    /* ── Sidebar ──────────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {{
        background: {MCD_DARK} !important;
        border-right: 3px solid {MCD_YELLOW};
    }}
    section[data-testid="stSidebar"] * {{
        color: #FFFFFF;
    }}
    section[data-testid="stSidebar"] label {{
        color: #CCCCCC !important;
        font-size: 0.85rem !important;
    }}
    section[data-testid="stSidebar"] .stSlider [data-testid="stMarkdownContainer"] p {{
        color: #CCCCCC !important;
        font-size: 0.82rem;
    }}

    /* ── Tabs ─────────────────────────────────────────────────────────── */
    div[data-testid="stTabs"] button[data-baseweb="tab"] {{
        background: {MCD_CARD};
        border-radius: 8px 8px 0 0;
        padding: 10px 28px;
        font-weight: 600;
        font-size: 0.92rem;
        color: {MCD_DARK};
        border: none;
        margin-right: 4px;
    }}
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {{
        background: {MCD_RED} !important;
        color: white !important;
    }}
    div[data-testid="stTabs"] button[data-baseweb="tab"]:hover:not([aria-selected="true"]) {{
        background: #FFE9A0;
    }}
    div[data-testid="stTabsContent"] {{
        background: transparent;
    }}

    /* ── Buttons ──────────────────────────────────────────────────────── */
    button[data-testid="baseButton-primary"] {{
        background-color: {MCD_RED} !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 12px 36px !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(218,41,28,0.35) !important;
        transition: all 0.15s ease !important;
    }}
    button[data-testid="baseButton-primary"]:hover {{
        background-color: #b8211a !important;
        box-shadow: 0 6px 18px rgba(218,41,28,0.45) !important;
        transform: translateY(-1px) !important;
    }}
    button[data-testid="baseButton-secondary"] {{
        border: 2px solid {MCD_YELLOW} !important;
        color: {MCD_DARK} !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        background: white !important;
    }}
    button[data-testid="baseButton-secondary"]:hover {{
        background: {MCD_YELLOW} !important;
    }}

    /* ── Dataframe ────────────────────────────────────────────────────── */
    div[data-testid="stDataFrame"] {{
        border: 2px solid {MCD_BORDER};
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    }}

    /* ── Alerts ───────────────────────────────────────────────────────── */
    div[data-testid="stAlert"] {{
        border-radius: 10px;
    }}

    /* ── Custom components ────────────────────────────────────────────── */
    .mcd-page-header {{
        background: linear-gradient(135deg, {MCD_RED} 0%, #C0201A 100%);
        padding: 22px 28px;
        border-radius: 14px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 18px;
        box-shadow: 0 4px 20px rgba(218,41,28,0.28);
    }}
    .mcd-page-header-logo {{
        font-size: 52px;
        line-height: 1;
    }}
    .mcd-page-header-title {{
        color: {MCD_YELLOW};
        margin: 0;
        font-size: 1.7rem;
        font-weight: 800;
        letter-spacing: -0.3px;
    }}
    .mcd-page-header-sub {{
        color: rgba(255,255,255,0.82);
        margin: 5px 0 0;
        font-size: 0.9rem;
    }}

    /* Sidebar logo block */
    .mcd-sidebar-logo {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 4px 0 18px 0;
        border-bottom: 2px solid {MCD_YELLOW};
        margin-bottom: 18px;
    }}
    .mcd-sidebar-brand {{
        font-weight: 800;
        font-size: 1rem;
        color: {MCD_YELLOW};
        letter-spacing: 0.02em;
    }}
    .mcd-sidebar-section {{
        font-size: 0.73rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: {MCD_YELLOW};
        margin: 20px 0 8px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid rgba(255,199,44,0.25);
    }}
    .mcd-active-branch {{
        background: {MCD_RED};
        color: white;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-top: 10px;
        word-break: break-word;
        line-height: 1.4;
    }}

    /* KPI cards */
    .mcd-kpi {{
        background: {MCD_CARD};
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
        border-top: 4px solid {MCD_RED};
        text-align: center;
        height: 100%;
    }}
    .mcd-kpi-icon {{
        font-size: 1.8rem;
        margin-bottom: 8px;
    }}
    .mcd-kpi-value {{
        font-size: 2.2rem;
        font-weight: 800;
        color: {MCD_RED};
        line-height: 1;
        margin-bottom: 6px;
    }}
    .mcd-kpi-label {{
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: {MCD_MUTED};
    }}

    /* Section headers */
    .mcd-section-header {{
        background: {MCD_RED};
        color: white;
        padding: 12px 18px;
        border-radius: 10px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .mcd-section-icon {{
        font-size: 1.4rem;
    }}
    .mcd-section-title {{
        font-weight: 700;
        font-size: 1rem;
        margin: 0;
    }}
    .mcd-section-sub {{
        font-size: 0.82rem;
        color: rgba(255,255,255,0.8);
        margin: 2px 0 0;
    }}

    /* Chart titles */
    .mcd-chart-title {{
        font-weight: 700;
        font-size: 0.95rem;
        color: {MCD_DARK};
        border-left: 4px solid {MCD_RED};
        padding-left: 10px;
        margin: 0 0 10px 0;
    }}

    /* Divider */
    .mcd-divider {{
        border: none;
        border-top: 2px solid {MCD_BORDER};
        margin: 20px 0;
        opacity: 1;
    }}

    /* Copilot header bar */
    .mcd-copilot-header {{
        background: {MCD_YELLOW};
        color: {MCD_DARK};
        font-weight: 800;
        font-size: 1.05rem;
        padding: 12px 18px;
        border-radius: 10px;
        margin-bottom: 6px;
    }}
    .mcd-copilot-meta {{
        font-size: 0.85rem;
        color: {MCD_MUTED};
        margin-bottom: 16px;
    }}

    /* Insight cards */
    .mcd-insights-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-bottom: 16px;
    }}
    .mcd-insight-card {{
        background: {MCD_CARD};
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        overflow: hidden;
    }}
    .mcd-card-header {{
        padding: 12px 16px;
        font-weight: 700;
        font-size: 0.92rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .mcd-card-summary .mcd-card-header  {{ background: {MCD_RED}; color: white; }}
    .mcd-card-actions .mcd-card-header  {{ background: {MCD_YELLOW}; color: {MCD_DARK}; }}
    .mcd-card-briefing .mcd-card-header {{ background: {MCD_DARK}; color: white; }}
    .mcd-card-body {{
        padding: 16px 18px;
        font-size: 0.9rem;
        line-height: 1.65;
        color: {MCD_DARK};
    }}
    .mcd-card-badge {{
        margin-left: auto;
        background: {MCD_YELLOW};
        color: {MCD_DARK};
        font-size: 0.68rem;
        padding: 3px 9px;
        border-radius: 12px;
        font-weight: 700;
        letter-spacing: 0.03em;
    }}
    .mcd-briefing-body {{
        font-family: 'Georgia', serif;
        background: {MCD_LIGHT};
        font-size: 0.88rem;
        line-height: 1.75;
    }}
    .mcd-action-item {{
        margin-bottom: 14px;
        padding-bottom: 14px;
        border-bottom: 1px solid {MCD_BORDER};
    }}
    .mcd-action-item:last-child {{
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
    }}
    .mcd-action-problem {{
        font-weight: 700;
        color: {MCD_DARK};
        margin-bottom: 4px;
    }}
    .mcd-action-evidence {{
        border-left: 3px solid {MCD_YELLOW};
        padding-left: 10px;
        font-style: italic;
        color: #555;
        margin: 6px 0;
        font-size: 0.87rem;
    }}
    .mcd-action-directive {{
        color: {MCD_RED};
        font-weight: 600;
        font-size: 0.87rem;
    }}
    .mcd-empty {{
        color: {MCD_MUTED};
        font-style: italic;
    }}

    /* ── Selectbox: selected value text inside the sidebar input box ─────── */
    section[data-testid="stSidebar"] [data-baseweb="select"] span,
    section[data-testid="stSidebar"] [data-baseweb="select"] div,
    section[data-testid="stSidebar"] [data-baseweb="select"] input {{
        color: #333333 !important;
    }}

    /* ── Selectbox dropdown (renders outside sidebar, white bg) ─────────── */
    [data-baseweb="popover"] [role="option"],
    [data-baseweb="popover"] li,
    [data-baseweb="menu"] [role="option"] {{
        color: {MCD_DARK} !important;
    }}

    /* Reviews Used table header */
    .mcd-table-header {{
        font-weight: 700;
        font-size: 0.92rem;
        color: {MCD_DARK};
        border-left: 4px solid {MCD_YELLOW};
        padding-left: 10px;
        margin: 4px 0 10px 0;
    }}
    </style>
    """, unsafe_allow_html=True)


_inject_css()

# ---------------------------------------------------------------------------
# Page header banner
# ---------------------------------------------------------------------------

st.markdown("""
<div class="mcd-page-header">
    <div class="mcd-page-header-logo">🍔</div>
    <div>
        <div class="mcd-page-header-title">McDonald's Social Media Command Centre</div>
        <div class="mcd-page-header-sub">Real-time review analytics &amp; AI-powered branch insights</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

df = data_loader.get_df()
all_cities  = sorted(df["city"].dropna().unique().tolist())
all_streets = sorted(df["street"].dropna().unique().tolist())

# ---------------------------------------------------------------------------
# Sidebar — logo (rendered once, before tabs)
# ---------------------------------------------------------------------------

st.sidebar.markdown("""
<div class="mcd-sidebar-logo">
    <span style="font-size:1.8rem;">🍔</span>
    <span class="mcd-sidebar-brand">MCD Command Centre</span>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_health_table(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("street", sort=False)
        .agg(City=("city", "first"), avg_rating=("rating", "mean"), total_reviews=("rating", "count"))
        .reset_index()
        .rename(columns={"street": "Branch", "total_reviews": "Total Reviews"})
    )

    recent = df[df["total_days_ago"] <= 30].groupby("street")["rating"].mean()
    prev   = df[(df["total_days_ago"] > 30) & (df["total_days_ago"] <= 60)].groupby("street")["rating"].mean()

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
    summary["Status"]     = summary["avg_rating"].apply(_status)
    summary["Trend"]      = summary["Branch"].apply(_trend)

    return (
        summary[["Branch", "City", "Avg Rating", "Total Reviews", "Status", "Trend"]]
        .sort_values("Avg Rating")
        .reset_index(drop=True)
    )


def _kpi_card(label: str, value: str, icon: str) -> str:
    return f"""
    <div class="mcd-kpi">
        <div class="mcd-kpi-icon">{icon}</div>
        <div class="mcd-kpi-value">{value}</div>
        <div class="mcd-kpi-label">{label}</div>
    </div>
    """


def _apply_chart_theme(fig, ax) -> None:
    fig.patch.set_facecolor(MCD_CARD)
    ax.set_facecolor("#FFF8F0")
    for spine in ax.spines.values():
        spine.set_color(MCD_BORDER)
    ax.tick_params(colors=MCD_DARK, labelsize=9)
    ax.title.set_color(MCD_DARK)
    ax.title.set_fontsize(11)
    ax.title.set_fontweight("bold")
    if ax.get_xlabel():
        ax.xaxis.label.set_color(MCD_MUTED)
        ax.xaxis.label.set_fontsize(9)
    if ax.get_ylabel():
        ax.yaxis.label.set_color(MCD_MUTED)
        ax.yaxis.label.set_fontsize(9)


def _parse_sections(result: str) -> dict:
    """Split Claude response into SUMMARY / ACTION ITEMS / STAFF BRIEFING."""
    headers = ["SUMMARY", "ACTION ITEMS", "STAFF BRIEFING"]
    pattern = r"(?mi)^(" + "|".join(re.escape(h) for h in headers) + r")\s*$"
    parts = re.split(pattern, result.strip(), flags=re.IGNORECASE)
    out = {h: "" for h in headers}
    i = 1
    while i < len(parts) - 1:
        key = parts[i].strip().upper()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if key in out:
            out[key] = body
        i += 2
    return out


def _format_action_items(text: str) -> str:
    """Convert numbered action item text into styled HTML."""
    if not text:
        return '<p class="mcd-empty">No action items available.</p>'
    lines = [l for l in text.splitlines() if l.strip()]
    html_parts = []
    current_item_lines = []

    def _flush(item_lines):
        if not item_lines:
            return ""
        full = " ".join(item_lines)
        m = re.match(r"^(\d+)\.\s+(.*)", full)
        if not m:
            return f'<div class="mcd-action-item"><p>{full}</p></div>'
        body = m.group(2)
        # Split on " — " separator used by the prompt format
        seg = re.split(r"\s+[—\-]{1,2}\s+", body, maxsplit=2)
        problem  = seg[0].strip() if len(seg) > 0 else body
        evidence = seg[1].strip() if len(seg) > 1 else ""
        action   = seg[2].strip() if len(seg) > 2 else ""
        # Strip "Evidence:" and "Action:" prefixes if present
        evidence = re.sub(r"^Evidence:\s*", "", evidence, flags=re.IGNORECASE).strip('"')
        action   = re.sub(r"^Action:\s*", "", action, flags=re.IGNORECASE)
        num = m.group(1)
        out = f'<div class="mcd-action-item">'
        out += f'<div class="mcd-action-problem">#{num} — {problem}</div>'
        if evidence:
            out += f'<div class="mcd-action-evidence">"{evidence}"</div>'
        if action:
            out += f'<div class="mcd-action-directive">→ {action}</div>'
        out += "</div>"
        return out

    for line in lines:
        if re.match(r"^\d+\.\s+", line) and current_item_lines:
            html_parts.append(_flush(current_item_lines))
            current_item_lines = [line]
        else:
            current_item_lines.append(line)
    html_parts.append(_flush(current_item_lines))
    return "\n".join(html_parts)


def _render_insights_cards(sections: dict) -> None:
    """Render SUMMARY and ACTION ITEMS as a two-column grid, STAFF BRIEFING below."""
    summary_html   = sections.get("SUMMARY", "") or '<p class="mcd-empty">Not available.</p>'
    action_html    = _format_action_items(sections.get("ACTION ITEMS", ""))
    briefing_text  = sections.get("STAFF BRIEFING", "") or "Not available."

    # Summary & Action Items — side by side
    st.markdown(f"""
    <div class="mcd-insights-grid">
        <div class="mcd-insight-card mcd-card-summary">
            <div class="mcd-card-header">
                <span>📋</span> Summary
            </div>
            <div class="mcd-card-body">{summary_html}</div>
        </div>
        <div class="mcd-insight-card mcd-card-actions">
            <div class="mcd-card-header">
                <span>⚡</span> Action Items
            </div>
            <div class="mcd-card-body">{action_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Staff Briefing — full width; convert markdown bold/italic to HTML
    briefing_html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", briefing_text)
    briefing_html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", briefing_html)
    briefing_escaped = briefing_html.replace("\n", "<br>")
    st.markdown(f"""
    <div class="mcd-insight-card mcd-card-briefing" style="margin-bottom:16px;">
        <div class="mcd-card-header">
            <span>📢</span> Staff Briefing
            <span class="mcd-card-badge">Ready to share</span>
        </div>
        <div class="mcd-card-body mcd-briefing-body">{briefing_escaped}</div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab1, tab2 = st.tabs(["📊  Review Dashboard", "🤖  AI Manager Co-Pilot"])

# ===========================================================================
# TAB 1 — Review Dashboard
# ===========================================================================

with tab1:
    # Sidebar — Dashboard filters
    st.sidebar.markdown('<div class="mcd-sidebar-section">📊 Dashboard Filters</div>', unsafe_allow_html=True)
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
        # ── KPI row ─────────────────────────────────────────────────────
        c1, c2, c3 = st.columns(3)
        c1.markdown(_kpi_card("Total Reviews", f"{len(dash_df):,}", "📝"), unsafe_allow_html=True)
        c2.markdown(_kpi_card("Avg Star Rating", f"{dash_df['rating'].mean():.2f} ★", "⭐"), unsafe_allow_html=True)
        c3.markdown(_kpi_card("Cities Covered", str(dash_df["city"].nunique()), "🏙️"), unsafe_allow_html=True)

        st.markdown('<hr class="mcd-divider">', unsafe_allow_html=True)

        # ── Row 1: Rating distribution + Review length ───────────────
        row1_left, row1_right = st.columns(2)

        with row1_left:
            st.markdown('<p class="mcd-chart-title">Rating Distribution</p>', unsafe_allow_html=True)
            rating_counts = (
                dash_df["rating"]
                .value_counts()
                .sort_index()
                .reset_index()
            )
            rating_counts.columns = ["rating", "count"]
            fig, ax = plt.subplots(figsize=(5, 3.5))
            _apply_chart_theme(fig, ax)
            ax.bar(
                rating_counts["rating"].astype(str),
                rating_counts["count"],
                color=MCD_RED,
                edgecolor=MCD_YELLOW,
                linewidth=0.8,
            )
            ax.set_xlabel("Rating")
            ax.set_ylabel("Number of Reviews")
            ax.set_title("Reviews by Star Rating")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        with row1_right:
            st.markdown('<p class="mcd-chart-title">Top 10 Best Performing Branches</p>', unsafe_allow_html=True)
            top_branches = (
                dash_df.groupby("street")
                .agg(avg_rating=("rating", "mean"), review_count=("rating", "count"), city=("city", "first"))
                .reset_index()
                .query("review_count >= 10")
                .nlargest(10, "avg_rating")
                .sort_values("avg_rating", ascending=True)
            )
            top_branches["label"] = top_branches["street"].str[:28] + "  (" + top_branches["city"] + ")"
            fig, ax = plt.subplots(figsize=(5, 3.5))
            _apply_chart_theme(fig, ax)
            colors = [MCD_YELLOW if v >= 4.5 else MCD_RED for v in top_branches["avg_rating"]]
            bars = ax.barh(top_branches["label"], top_branches["avg_rating"], color=colors, edgecolor="white")
            ax.set_xlim(0, 5)
            ax.axvline(x=3.5, color=MCD_DARK, linestyle="--", linewidth=1, alpha=0.5)
            for bar, val in zip(bars, top_branches["avg_rating"]):
                ax.text(val + 0.05, bar.get_y() + bar.get_height() / 2, f"{val:.2f}", va="center", fontsize=8, color=MCD_DARK)
            ax.set_xlabel("Avg Rating")
            ax.set_title("Top 10 Branches by Avg Rating (min. 10 reviews)")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        st.markdown('<hr class="mcd-divider">', unsafe_allow_html=True)

        # ── Row 2: Top cities + Correlation heatmap ──────────────────
        row2_left, row2_right = st.columns(2)

        with row2_left:
            st.markdown('<p class="mcd-chart-title">Top 10 Cities by Review Count</p>', unsafe_allow_html=True)
            top_cities = (
                dash_df["city"]
                .value_counts()
                .head(10)
                .sort_values(ascending=True)
                .reset_index()
            )
            top_cities.columns = ["city", "count"]
            fig, ax = plt.subplots(figsize=(5, 3.5))
            _apply_chart_theme(fig, ax)
            bars = ax.barh(top_cities["city"], top_cities["count"], color=MCD_RED, edgecolor="white")
            # Highlight top bar in yellow
            if len(bars):
                bars[-1].set_facecolor(MCD_YELLOW)
                bars[-1].set_edgecolor(MCD_RED)
            ax.set_xlabel("Number of Reviews")
            ax.set_title("Top 10 Cities")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        with row2_right:
            st.markdown('<p class="mcd-chart-title">Worst Performing Branches</p>', unsafe_allow_html=True)
            branch_avg = (
                dash_df.groupby("street")
                .agg(avg_rating=("rating", "mean"), city=("city", "first"))
                .reset_index()
                .nsmallest(5, "avg_rating")
                .sort_values("avg_rating", ascending=True)
            )
            branch_avg["label"] = branch_avg["street"].str[:28] + "  (" + branch_avg["city"] + ")"
            fig, ax = plt.subplots(figsize=(5, 3.5))
            _apply_chart_theme(fig, ax)
            colors = [MCD_RED if v < 2.5 else MCD_YELLOW for v in branch_avg["avg_rating"]]
            bars = ax.barh(branch_avg["label"], branch_avg["avg_rating"], color=colors, edgecolor="white")
            ax.set_xlim(0, 5)
            ax.axvline(x=2.5, color=MCD_DARK, linestyle="--", linewidth=1, alpha=0.5)
            for bar, val in zip(bars, branch_avg["avg_rating"]):
                ax.text(val + 0.05, bar.get_y() + bar.get_height() / 2, f"{val:.2f}", va="center", fontsize=8, color=MCD_DARK)
            ax.set_xlabel("Avg Rating")
            ax.set_title("Bottom 5 Branches by Avg Rating")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

# ===========================================================================
# TAB 2 — AI Manager Co-Pilot
# ===========================================================================

with tab2:
    # ── Branch Health Overview ───────────────────────────────────────────
    # IMPORTANT: table + row-click detection must run BEFORE the sidebar
    # selectbox so session_state["copilot_branch"] is set in time.
    st.markdown("""
    <div class="mcd-section-header">
        <span class="mcd-section-icon">📊</span>
        <div>
            <div class="mcd-section-title">Branch Health Overview</div>
            <div class="mcd-section-sub">Click any row to load that branch in the Co-Pilot below.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    health_df    = _build_health_table(df)
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

    st.markdown('<hr class="mcd-divider">', unsafe_allow_html=True)

    # ── Co-Pilot Filters (sidebar) ───────────────────────────────────────
    st.sidebar.markdown('<div class="mcd-sidebar-section">🤖 Co-Pilot Filters</div>', unsafe_allow_html=True)
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
    st.sidebar.markdown(
        f'<div class="mcd-active-branch">📍 {selected_branch}</div>',
        unsafe_allow_html=True,
    )

    # ── Co-Pilot main area ───────────────────────────────────────────────
    filtered    = data_loader.filter_reviews(df, selected_branch, days_range)
    num_reviews = len(filtered)

    st.markdown(
        f'<div class="mcd-copilot-header">🤖 AI Manager Co-Pilot — {selected_branch}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="mcd-copilot-meta">Showing reviews from the last <strong>{days_range} days</strong> &nbsp;·&nbsp; '
        f'<strong>{num_reviews}</strong> matching review{"s" if num_reviews != 1 else ""} found</p>',
        unsafe_allow_html=True,
    )

    if num_reviews == 0:
        st.warning(
            f"No reviews found for **{selected_branch}** in the last {days_range} days. "
            "Try a different branch or extend the time range."
        )
    else:
        col_btn, col_hint = st.columns([1, 3])
        with col_btn:
            run_insights = st.button("Generate Insights", type="primary", use_container_width=True)
        with col_hint:
            st.caption(f"Sends up to 20 most recent reviews to Claude for analysis.")

        if run_insights:
            with st.spinner("Analysing reviews with Claude..."):
                result = llm.generate_insights(filtered, selected_branch, days_range)

            sections = _parse_sections(result)
            _render_insights_cards(sections)

            briefing_text = sections.get("STAFF BRIEFING", "")
            if briefing_text:
                safe_name = re.sub(r"[^\w\-]", "_", selected_branch)
                filename  = f"briefing_{safe_name}_{date.today()}.txt"
                clean_briefing = re.sub(r"\*+", "", briefing_text)
                st.download_button(
                    label="⬇️  Download Staff Briefing (.txt)",
                    data=clean_briefing,
                    file_name=filename,
                    mime="text/plain",
                )

        st.markdown('<hr class="mcd-divider">', unsafe_allow_html=True)

        # ── Reviews preview ──────────────────────────────────────────────
        st.markdown('<p class="mcd-table-header">Reviews Used for Analysis</p>', unsafe_allow_html=True)
        display_cols = [c for c in ["rating", "review"] if c in filtered.columns]
        preview = (
            filtered.sort_values("total_days_ago", ascending=True)
            [display_cols]
            .head(50)
            .reset_index(drop=True)
            .rename(columns={"rating": "Rating", "review": "Review"})
        )
        preview.index += 1
        st.dataframe(preview, use_container_width=True)
