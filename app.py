from pathlib import Path
import base64

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.cleaning import load_data


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Google Play Analytics",
    page_icon="▶",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# GOOGLE PLAY / DARK THEME
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&family=Roboto:wght@400;500;700&display=swap');

    :root {
        --bg: #000000;
        --surface: #0d0d0d;
        --surface2: #151515;
        --border: #2a2a2a;
        --text: #ffffff;
        --muted: #a7a7a7;
        --green: #34a853;
        --blue: #4285f4;
        --yellow: #fbbc05;
        --red: #ea4335;
    }

    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 80% -10%, rgba(66,133,244,.14), transparent 28%),
            radial-gradient(circle at 5% 20%, rgba(52,168,83,.08), transparent 25%),
            #000000;
        color: #ffffff;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: rgba(0,0,0,.92);
    }

    .block-container {
        max-width: 1500px;
        padding: 1.4rem 2.2rem 3rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #070707;
        border-right: 1px solid #242424;
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 1.2rem 1rem;
    }

    section[data-testid="stSidebar"] * {
        color: #ffffff;
    }

    /* Brand */
    .brand {
        display: flex;
        align-items: center;
        gap: 13px;
        padding: 4px 2px 24px;
    }

    .google-g {
        font-family: Arial, sans-serif;
        font-size: 38px;
        font-weight: 800;
        line-height: 1;
        background: conic-gradient(
            from 210deg,
            #4285f4 0deg 95deg,
            #34a853 95deg 180deg,
            #fbbc05 180deg 245deg,
            #ea4335 245deg 315deg,
            #4285f4 315deg 360deg
        );
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    .brand-name {
        font-family: 'Google Sans', sans-serif;
        font-size: 20px;
        font-weight: 600;
        letter-spacing: -.3px;
        color: #fff;
    }

    .brand-name span {
        color: #9aa0a6;
        font-weight: 400;
    }

    .sidebar-card {
        background: #101010;
        border: 1px solid #292929;
        border-radius: 16px;
        padding: 15px;
        margin-top: 18px;
        color: #aeb0b3;
        font-size: 12px;
        line-height: 1.55;
    }

    /* Hero */
    .hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #101010 0%, #080808 55%, #111827 100%);
        border: 1px solid #292929;
        border-radius: 24px;
        padding: 32px 34px;
        margin-bottom: 22px;
        box-shadow: 0 18px 60px rgba(0,0,0,.55);
    }

    .hero:after {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        right: -90px;
        top: -110px;
        border-radius: 50%;
        background: rgba(66,133,244,.12);
        filter: blur(12px);
    }

    .hero-top {
        display: flex;
        align-items: center;
        gap: 18px;
        position: relative;
        z-index: 1;
    }

    .play-mark {
        width: 66px;
        height: 66px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #111111;
        border: 1px solid #343434;
        box-shadow: 0 10px 30px rgba(0,0,0,.5);
    }

    .play-triangle {
        width: 0;
        height: 0;
        border-top: 18px solid transparent;
        border-bottom: 18px solid transparent;
        border-left: 29px solid #34a853;
        margin-left: 5px;
        filter: drop-shadow(0 0 8px rgba(52,168,83,.25));
    }

    .hero-title {
        font-family: 'Google Sans', sans-serif;
        color: #ffffff;
        font-size: 36px;
        font-weight: 700;
        letter-spacing: -.9px;
        line-height: 1.15;
    }

    .hero-subtitle {
        color: #a9adb2;
        margin-top: 8px;
        font-size: 14px;
    }

    .section-title {
        font-family: 'Google Sans', sans-serif;
        color: #ffffff;
        font-size: 21px;
        font-weight: 600;
        margin: 26px 0 13px;
    }

    /* KPI cards */
    .metric-card {
        background: linear-gradient(145deg, #111111, #0a0a0a);
        border: 1px solid #292929;
        border-radius: 17px;
        padding: 20px;
        min-height: 120px;
        box-shadow: 0 10px 30px rgba(0,0,0,.28);
    }

    .metric-label {
        color: #9aa0a6;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
    }

    .metric-value {
        color: #ffffff;
        font-family: 'Google Sans', sans-serif;
        font-size: 29px;
        font-weight: 700;
        margin-top: 9px;
    }

    .metric-note {
        color: #777b80;
        font-size: 11px;
        margin-top: 7px;
    }

    /* Plot container */
    .chart-card {
        background: #0c0c0c;
        border: 1px solid #292929;
        border-radius: 18px;
        padding: 10px 10px 2px;
        box-shadow: 0 12px 35px rgba(0,0,0,.35);
    }

    /* Inputs */
    div[data-baseweb="select"] > div {
        background-color: #111111 !important;
        border-color: #333333 !important;
        color: #ffffff !important;
    }

    .stMultiSelect [data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] span {
        color: #ffffff !important;
    }

    .stButton > button {
        background: #111111;
        color: #ffffff;
        border: 1px solid #343434;
        border-radius: 12px;
        font-weight: 500;
    }

    .stButton > button:hover {
        border-color: #4285f4;
        color: #ffffff;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #292929;
        border-radius: 14px;
        overflow: hidden;
    }

    /* Captions / markdown */
    .stCaption, .stMarkdown p {
        color: #b0b3b8;
    }

    /* Divider */
    hr {
        border-color: #252525 !important;
    }

    .footer {
        text-align: center;
        color: #666a70;
        font-size: 11px;
        padding: 30px 0 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data(show_spinner=False)
def get_data():
    return load_data()


try:
    df = get_data()
except Exception as exc:
    st.error("Unable to load the Google Play Store dataset.")
    st.info("Check your dataset path and utils.cleaning.load_data() configuration.")
    with st.expander("Technical details"):
        st.code(str(exc))
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="google-g">G</div>
            <div class="brand-name">Google <span>Play Analytics</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Navigation")
    view = st.radio(
        "Navigation",
        ["Dashboard", "Dataset Preview"],
        label_visibility="collapsed",
    )

    st.markdown(
        """
        <div class="sidebar-card">
            <b style="color:#fff;">Play Store Intelligence</b><br><br>
            Explore application categories, ratings, reviews and installation
            patterns through an interactive analytics workspace.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HERO
# ============================================================
st.markdown(
    """
    <div class="hero">
        <div class="hero-top">
            <div class="play-mark">
                <div class="play-triangle"></div>
            </div>
            <div>
                <div class="hero-title">Google Play Store Analytics</div>
                <div class="hero-subtitle">
                    Application intelligence • Category performance • User engagement
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# METRICS
# ============================================================
rating_col = next((c for c in ["Rating", "rating"] if c in df.columns), None)
reviews_col = next((c for c in ["Reviews", "reviews"] if c in df.columns), None)
category_col = next((c for c in ["Category", "category"] if c in df.columns), None)

avg_rating = (
    pd.to_numeric(df[rating_col], errors="coerce").mean()
    if rating_col else None
)

total_reviews = (
    pd.to_numeric(
        df[reviews_col].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    ).sum()
    if reviews_col else None
)

category_count = df[category_col].nunique() if category_col else None


def compact(value):
    if value is None or pd.isna(value):
        return "—"
    value = float(value)
    if value >= 1_000_000_000:
        return f"{value/1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value/1_000:.1f}K"
    return f"{value:,.0f}"


st.markdown(
    '<div class="section-title">Platform Overview</div>',
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)

cards = [
    ("TOTAL APPLICATIONS", f"{len(df):,}", "Apps in the dataset"),
    ("AVERAGE RATING", f"{avg_rating:.2f}" if avg_rating is not None and not pd.isna(avg_rating) else "—", "Across rated apps"),
    ("CATEGORIES", str(category_count) if category_count is not None else "—", "Distinct app categories"),
    ("TOTAL REVIEWS", compact(total_reviews), "Combined review volume"),
]

for col, (label, value, note) in zip([c1, c2, c3, c4], cards):
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# DASHBOARD
# ============================================================
if view == "Dashboard":

    left, right = st.columns([1.45, 1])

    with left:
        st.markdown(
            '<div class="section-title">Top Application Categories</div>',
            unsafe_allow_html=True,
        )

        if category_col:
            counts = (
                df[category_col]
                .astype(str)
                .value_counts()
                .head(10)
                .sort_values()
            )

            fig = px.bar(
                x=counts.values,
                y=counts.index,
                orientation="h",
                labels={"x": "Applications", "y": ""},
                template="plotly_dark",
            )

            fig.update_traces(
                marker_color="#34a853",
                hovertemplate="<b>%{y}</b><br>Apps: %{x:,}<extra></extra>",
            )

            fig.update_layout(
                height=440,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ffffff"),
                margin=dict(l=10, r=20, t=15, b=20),
                xaxis=dict(
                    gridcolor="#242424",
                    zerolinecolor="#333333",
                ),
                yaxis=dict(
                    gridcolor="rgba(0,0,0,0)",
                ),
            )

            st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown(
            '<div class="section-title">Data Quality</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="metric-card" style="min-height:190px;">
                <div class="metric-label">DATASET STATUS</div>
                <div class="metric-value" style="font-size:22px;">● Ready</div>
                <div class="metric-note">
                    Rows: {len(df):,}<br>
                    Columns: {len(df.columns):,}<br>
                    Missing values: {int(df.isna().sum().sum()):,}<br>
                    Duplicate rows: {int(df.duplicated().sum()):,}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if rating_col:
            ratings = pd.to_numeric(df[rating_col], errors="coerce").dropna()

            if not ratings.empty:
                st.markdown(
                    '<div class="section-title">Rating Distribution</div>',
                    unsafe_allow_html=True,
                )

                fig2 = px.histogram(
                    x=ratings,
                    nbins=20,
                    labels={"x": "Rating"},
                    template="plotly_dark",
                )

                fig2.update_traces(
                    marker_color="#4285f4",
                    hovertemplate="Rating: %{x}<br>Apps: %{y}<extra></extra>",
                )

                fig2.update_layout(
                    height=260,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#ffffff"),
                    margin=dict(l=10, r=10, t=10, b=25),
                    xaxis=dict(gridcolor="#242424"),
                    yaxis=dict(gridcolor="#242424"),
                )

                st.plotly_chart(fig2, use_container_width=True)

else:
    st.markdown(
        '<div class="section-title">Dataset Preview</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(
        df.head(100),
        use_container_width=True,
        height=560,
        hide_index=True,
    )


# ============================================================
# FOOTER
# ============================================================
st.markdown(
    """
    <div class="footer">
        Google Play Analytics • Dark Intelligence Dashboard
    </div>
    """,
    unsafe_allow_html=True,
)
