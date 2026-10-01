
import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.cleaning import load_data  # type: ignore[reportMissingImports]
from utils.time_control import check_time  # type: ignore[reportMissingImports]

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Google Play | Sunburst Intelligence",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# PROFESSIONAL DARK THEME
# --------------------------------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #0b0f14;
        color: #f4f7fb;
    }

    [data-testid="stSidebar"] {
        background: #111720;
        border-right: 1px solid #26313d;
    }

    [data-testid="stSidebar"] * {
        color: #e5edf5;
    }

    .hero {
        background: linear-gradient(120deg, #172b30, #14232b 55%, #17202d);
        border: 1px solid #29443f;
        padding: 28px 32px;
        border-radius: 18px;
        margin: 8px 0 24px 0;
    }

    .hero-label {
        color: #55d6a5;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .hero h1 {
        font-size: 30px;
        font-weight: 800;
        color: #ffffff;
        margin: 12px 0 8px 0;
    }

    .hero p {
        color: #b4c4d0;
        font-size: 14px;
        margin: 0;
    }

    .section-title {
        font-size: 19px;
        font-weight: 700;
        color: #f4f7fb;
        margin: 22px 0 14px 0;
    }

    .metric-card {
        background: linear-gradient(145deg, #171f29, #121922);
        border: 1px solid #283541;
        border-radius: 15px;
        padding: 20px;
        min-height: 120px;
    }

    .metric-label {
        font-size: 12px;
        font-weight: 600;
        color: #9eafbf;
        margin-bottom: 12px;
    }

    .metric-value {
        font-size: 27px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.7px;
    }

    .metric-note {
        font-size: 11px;
        color: #57d5a1;
        margin-top: 7px;
    }

    .insight-card {
        background: #141c25;
        border: 1px solid #283541;
        border-left: 3px solid #42c997;
        border-radius: 10px;
        padding: 16px 18px;
        min-height: 100px;
    }

    .insight-label {
        color: #9eafbf;
        font-size: 12px;
        font-weight: 600;
    }

    .insight-value {
        color: #ffffff;
        font-size: 19px;
        font-weight: 700;
        margin-top: 9px;
    }

    .footer {
        color: #82909e;
        font-size: 11px;
        text-align: center;
        padding: 20px 0 5px 0;
        border-top: 1px solid #283541;
        margin-top: 30px;
    }

    div[data-testid="stPlotlyChart"] {
        background: #111720;
        border: 1px solid #283541;
        border-radius: 16px;
        padding: 10px;
    }

    div[data-testid="stMetric"] {
        background: #171f29;
        border: 1px solid #283541;
        padding: 14px;
        border-radius: 12px;
    }

    .stButton button {
        border-radius: 9px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# TIME RESTRICTION
# --------------------------------------------------

if not check_time(18, 20):
    st.warning(
        "This analytics page is available between "
        "6 PM and 8 PM IST."
    )
    st.stop()

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data(show_spinner="Loading and preparing app data...")
def get_data():
    data = load_data().copy()

    required = [
        "App", "Category", "Rating", "Reviews",
        "Installs", "Size", "Type"
    ]

    missing = [c for c in required if c not in data.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    for col in ["Rating", "Reviews", "Installs", "Size"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data["App"] = data["App"].astype("string").str.strip()
    data["Category"] = data["Category"].astype("string").str.strip()
    data["Type"] = data["Type"].fillna("Unknown").astype(str)

    data = data.dropna(
        subset=[
            "App", "Category", "Rating",
            "Reviews", "Installs", "Size"
        ]
    )

    return data

try:
    raw_df = get_data()
except Exception as e:
    st.error(f"Dataset loading error: {e}")
    st.stop()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.markdown("## 🟢 Play Store Analytics")
st.sidebar.caption("SUNBURST INTELLIGENCE")
st.sidebar.divider()

st.sidebar.markdown("### Analysis Controls")

min_rating = st.sidebar.slider(
    "Minimum rating",
    min_value=1.0,
    max_value=5.0,
    value=4.0,
    step=0.1
)

min_installs = st.sidebar.select_slider(
    "Minimum installs",
    options=[0, 1000, 10000, 50000, 100000, 500000, 1000000],
    value=10000,
    format_func=lambda x: f"{x:,}"
)

categories = sorted(
    raw_df["Category"].dropna().unique().tolist()
)

selected_categories = st.sidebar.multiselect(
    "Categories",
    options=categories,
    default=categories
)

exclude_numeric = st.sidebar.checkbox(
    "Exclude app names containing numbers",
    value=True
)

st.sidebar.divider()

if st.sidebar.button("Reset filters", use_container_width=True):
    st.rerun()

# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------

df = raw_df[
    (raw_df["Rating"] >= min_rating) &
    (raw_df["Installs"] >= min_installs) &
    (raw_df["Reviews"] > 0) &
    (raw_df["Size"].between(15, 80)) &
    (raw_df["Category"].isin(selected_categories))
].copy()

if exclude_numeric:
    df = df[
        ~df["App"].str.contains(r"\d", na=False)
    ].copy()

if df.empty:
    st.warning(
        "No records match the selected filters. "
        "Please adjust the filters."
    )
    st.stop()

# --------------------------------------------------
# RATING BANDS
# --------------------------------------------------

df["Rating Band"] = pd.cut(
    df["Rating"],
    bins=[3.99, 4.2, 4.5, 4.7, 5.0],
    labels=[
        "4.0–4.2",
        "4.2–4.5",
        "4.5–4.7",
        "4.7–5.0"
    ],
    include_lowest=True
)

df["Rating Band"] = df["Rating Band"].astype(str)
df["App Type"] = df["Type"].replace({
    "Free": "Free Apps",
    "Paid": "Paid Apps"
})

# --------------------------------------------------
# HERO HEADER
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <div class="hero-label">Google Play Store · Data Intelligence</div>
    <h1>Hierarchical Sunburst Analysis</h1>
    <p>
        Explore app install distribution, category performance,
        rating segments, and app-type composition.
    </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# KPI METRICS
# --------------------------------------------------

total_installs = df["Installs"].sum()
total_apps = df["App"].nunique()
avg_rating = df["Rating"].mean()
total_categories = df["Category"].nunique()

def compact_number(value):
    if value >= 1e9:
        return f"{value / 1e9:.2f}B"
    if value >= 1e6:
        return f"{value / 1e6:.2f}M"
    if value >= 1e3:
        return f"{value / 1e3:.1f}K"
    return f"{value:,.0f}"

k1, k2, k3, k4 = st.columns(4)

metrics = [
    (k1, "TOTAL INSTALLS", compact_number(total_installs), "Across filtered records"),
    (k2, "APPS ANALYZED", f"{total_apps:,}", "Unique app names"),
    (k3, "AVERAGE RATING", f"{avg_rating:.2f}/5", "Mean app rating"),
    (k4, "CATEGORIES", f"{total_categories:,}", "Selected categories")
]

for col, label, value, note in metrics:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """, unsafe_allow_html=True)

# --------------------------------------------------
# AGGREGATION
# --------------------------------------------------

group_cols = [
    "Category", "App Type", "Rating Band"
]

def weighted_rating(group):
    reviews = group["Reviews"].sum()
    if reviews <= 0:
        return 0.0
    return (
        (group["Rating"] * group["Reviews"]).sum() / reviews
    )

records = []

for keys, group in df.groupby(group_cols, observed=True):
    records.append({
        "Category": keys[0],
        "App Type": keys[1],
        "Rating Band": keys[2],
        "Total Installs": group["Installs"].sum(),
        "Total Reviews": group["Reviews"].sum(),
        "Weighted Rating": weighted_rating(group)
    })

sunburst_data = pd.DataFrame(records)

if sunburst_data.empty:
    st.warning("No data is available for the chart.")
    st.stop()

# --------------------------------------------------
# CHART SECTION
# --------------------------------------------------

st.markdown(
    '<div class="section-title">Install Distribution Explorer</div>',
    unsafe_allow_html=True
)

left, right = st.columns([3, 1])

with right:
    color_metric = st.selectbox(
        "Color by",
        ["Weighted Rating", "Total Reviews"],
        index=0
    )

    chart_height = st.select_slider(
        "Chart size",
        options=["Compact", "Standard", "Large"],
        value="Large"
    )

height_map = {
    "Compact": 480,
    "Standard": 600,
    "Large": 700
}

with left:
    st.caption(
        "Select a segment to zoom in. Use the center to navigate "
        "back through the hierarchy."
    )

    fig = px.sunburst(
        sunburst_data,
        path=[
            "Category",
            "App Type",
            "Rating Band"
        ],
        values="Total Installs",
        color=color_metric,
        color_continuous_scale=(
            "RdYlGn" if color_metric == "Weighted Rating"
            else "Teal"
        ),
        range_color=(
            [4, 5] if color_metric == "Weighted Rating"
            else None
        ),
        hover_data={
            "Total Installs": ":,",
            "Total Reviews": ":,",
            "Weighted Rating": ":.2f"
        }
    )

    fig.update_traces(
        branchvalues="total",
        insidetextorientation="radial",
        textinfo="label+percent parent",
        marker=dict(
            line=dict(
                color="#111720",
                width=2
            )
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Installs: %{value:,.0f}<br>"
            "Share of parent: %{percentParent}<br>"
            "<extra></extra>"
        ),
        maxdepth=3
    )

    fig.update_layout(
        height=height_map[chart_height],
        paper_bgcolor="#111720",
        plot_bgcolor="#111720",
        font=dict(
            family="Inter, sans-serif",
            color="#f4f7fb",
            size=12
        ),
        margin=dict(
            t=25, b=25, l=20, r=20
        ),
        coloraxis_colorbar=dict(
            title=color_metric,
            tickfont=dict(color="#dce5ed"),
            title_font=dict(color="#ffffff")
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "responsive": True,
            "scrollZoom": False
        }
    )

# --------------------------------------------------
# CATEGORY PERFORMANCE
# --------------------------------------------------

st.markdown(
    '<div class="section-title">Category Performance Insights</div>',
    unsafe_allow_html=True
)

category_stats = (
    df.groupby("Category")
    .agg(
        Installs=("Installs", "sum"),
        Apps=("App", "nunique"),
        Average_Rating=("Rating", "mean"),
        Reviews=("Reviews", "sum")
    )
    .sort_values("Installs", ascending=False)
)

top_category = category_stats.index[0]
top_installs = category_stats.iloc[0]["Installs"]

category_share = top_installs / total_installs * 100

i1, i2, i3 = st.columns(3)

insights = [
    (
        i1,
        "Highest-install category",
        top_category
    ),
    (
        i2,
        "Category install share",
        f"{category_share:.1f}%"
    ),
    (
        i3,
        "Highest category installs",
        compact_number(top_installs)
    )
]

for col, label, value in insights:
    with col:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">{label}</div>
            <div class="insight-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

# --------------------------------------------------
# CATEGORY DATA TABLE
# --------------------------------------------------

with st.expander("View detailed category performance"):
    display_stats = category_stats.reset_index().rename(
        columns={
            "Category": "Category",
            "Installs": "Total Installs",
            "Apps": "Unique Apps",
            "Average_Rating": "Average Rating",
            "Reviews": "Total Reviews"
        }
    )

    display_stats["Total Installs"] = (
        display_stats["Total Installs"].map(lambda x: f"{x:,.0f}")
    )
    display_stats["Total Reviews"] = (
        display_stats["Total Reviews"].map(lambda x: f"{x:,.0f}")
    )
    display_stats["Average Rating"] = (
        display_stats["Average Rating"].map(lambda x: f"{x:.2f}")
    )

    st.dataframe(
        display_stats,
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("""
<div class="footer">
    GOOGLE PLAY STORE ANALYTICS · SUNBURST INTELLIGENCE<br>
    Interactive Data Visualization | Streamlit + Plotly
</div>
""", unsafe_allow_html=True)