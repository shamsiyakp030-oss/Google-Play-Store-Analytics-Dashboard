# ============================================================
# 4_Streamgraph.py
# Google Play Store — Interactive Streamgraph Dashboard
# ============================================================

from pathlib import Path
from datetime import datetime, time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from zoneinfo import ZoneInfo


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Google Play Streamgraph Analytics",
    page_icon="🌊",
    layout="wide",
)


# ============================================================
# PROJECT / DATA PATH
# ============================================================

# File location:
# Project/
# ├── app.py
# ├── data/
# │   └── googleplaystore.csv
# └── pages/
#     └── 4_Streamgraph.py

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "googleplaystore.csv"


# ============================================================
# IST TIME RESTRICTION
# 6:00 PM - 9:00 PM IST
# ============================================================

IST = ZoneInfo("Asia/Kolkata")

ACCESS_START = time(18, 0)
ACCESS_END = time(21, 0)


def access_allowed():
    current_time = datetime.now(IST).time()
    return ACCESS_START <= current_time < ACCESS_END


if not access_allowed():

    current_time = datetime.now(IST)

    st.title("🌊 Google Play Streamgraph Analytics")

    st.warning(
        "This dashboard is available only between "
        "**6:00 PM and 9:00 PM IST**."
    )

    st.info(
        f"Current IST Time: "
        f"**{current_time.strftime('%I:%M:%S %p')}**"
    )

    st.stop()


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 25px;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(120,120,120,0.2);
        border-radius: 12px;
        padding: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CATEGORY TRANSLATIONS
# ============================================================

CATEGORY_TRANSLATIONS = {

    "ART_AND_DESIGN": "Art & Design",
    "AUTO_AND_VEHICLES": "Auto & Vehicles",
    "BEAUTY": "Beauty",
    "BOOKS_AND_REFERENCE": "Books & Reference",
    "BUSINESS": "Business",
    "COMICS": "Comics",
    "COMMUNICATION": "Communication",
    "DATING": "Dating",
    "EDUCATION": "Education",
    "ENTERTAINMENT": "Entertainment",
    "EVENTS": "Events",
    "FAMILY": "Family",
    "FINANCE": "Finance",
    "FOOD_AND_DRINK": "Food & Drink",
    "HEALTH_AND_FITNESS": "Health & Fitness",
    "HOUSE_AND_HOME": "House & Home",
    "LIBRARIES_AND_DEMO": "Libraries & Demo",
    "LIFESTYLE": "Lifestyle",
    "GAME": "Games",
    "MEDICAL": "Medical",
    "NEWS_AND_MAGAZINES": "News & Magazines",
    "PARENTING": "Parenting",
    "PERSONALIZATION": "Personalization",
    "PHOTOGRAPHY": "Photography",
    "PRODUCTIVITY": "Productivity",
    "SHOPPING": "Shopping",
    "SOCIAL": "Social",
    "SPORTS": "Sports",
    "TOOLS": "Tools",
    "TRAVEL_AND_LOCAL": "Travel & Local",
    "VIDEO_PLAYERS": "Video Players & Editors",
    "VIDEO_PLAYERS_AND_EDITORS": "Video Players & Editors",
    "WEATHER": "Weather",
}


def category_label(category):
    category = str(category).upper()

    return CATEGORY_TRANSLATIONS.get(
        category,
        category.replace("_", " ").title()
    )


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    if not DATA_FILE.exists():

        raise FileNotFoundError(
            f"Dataset not found at:\n{DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    required_columns = [
        "App",
        "Category",
        "Reviews",
        "Installs",
        "Last Updated",
    ]

    missing_columns = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    # --------------------------------------------------------
    # Reviews
    # --------------------------------------------------------

    df["Reviews"] = (
        df["Reviews"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(
            r"(\d+(?:\.\d+)?)",
            expand=False
        )
        .fillna("0")
        .astype(float)
    )

    # --------------------------------------------------------
    # Installs
    # Example: 1,000+ -> 1000
    # --------------------------------------------------------

    df["Install Count"] = (
        df["Installs"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(
            r"(\d+(?:\.\d+)?)",
            expand=False
        )
        .fillna("0")
        .astype(float)
    )

    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    df["Last Updated"] = pd.to_datetime(
        df["Last Updated"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Last Updated"]
    ).copy()

    # Remove duplicate app/category/date records.
    df = df.drop_duplicates(
        subset=[
            "App",
            "Category",
            "Last Updated"
        ],
        keep="first"
    )

    df["Month"] = (
        df["Last Updated"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    df["Category Display"] = (
        df["Category"]
        .apply(category_label)
    )

    return df


# ============================================================
# LOAD DATA WITH ERROR HANDLING
# ============================================================

try:

    df = load_data()

except FileNotFoundError:

    st.error(
        "❌ Could not find the dataset.\n\n"
        f"Expected location:\n`{DATA_FILE}`\n\n"
        "Make sure your project structure is:\n\n"
        "Project/\n"
        "├── app.py\n"
        "├── data/\n"
        "│   └── googleplaystore.csv\n"
        "└── pages/\n"
        "    └── 4_Streamgraph.py"
    )

    st.stop()

except Exception as error:

    st.error(
        f"❌ Dataset loading error:\n\n{error}"
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">'
    '🌊 Google Play Streamgraph Analytics'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Explore how Google Play Store categories change '
    'over time using an interactive streamgraph.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR CONTROLS
# ============================================================

with st.sidebar:

    st.header("🎛️ Streamgraph Controls")

    metric = st.selectbox(
        "Select Metric",
        [
            "App Count",
            "Reviews",
            "Install Lower Bound"
        ]
    )

    st.divider()

    categories = sorted(
        df["Category"].dropna().unique()
    )

    display_categories = [
        category_label(category)
        for category in categories
    ]

    selected_categories = st.multiselect(
        "Select Categories",
        options=display_categories,
        default=display_categories[:8]
        if len(display_categories) > 8
        else display_categories,
        help="Leave selections empty to display all categories."
    )

    if not selected_categories:

        selected_categories = display_categories

    st.divider()

    # Number of categories shown.
    max_categories = st.slider(
        "Maximum Categories",
        min_value=3,
        max_value=min(20, len(display_categories)),
        value=min(10, len(display_categories))
    )

    st.caption(
        "Access: 6:00 PM – 9:00 PM IST"
    )


# ============================================================
# METRIC PREPARATION
# ============================================================

if metric == "App Count":

    metric_column = "App"

elif metric == "Reviews":

    metric_column = "Reviews"

else:

    metric_column = "Install Count"


# Filter selected categories.
selected_category_codes = [
    category
    for category in categories
    if category_label(category)
    in selected_categories
]

filtered_df = df[
    df["Category"].isin(
        selected_category_codes
    )
].copy()


if filtered_df.empty:

    st.warning(
        "No records are available for the selected categories."
    )

    st.stop()


# ============================================================
# MONTHLY CATEGORY DATA
# ============================================================

if metric == "App Count":

    monthly_data = (
        filtered_df
        .groupby(
            ["Month", "Category"]
        )
        .agg(
            Value=("App", "nunique")
        )
        .reset_index()
    )

else:

    monthly_data = (
        filtered_df
        .groupby(
            ["Month", "Category"]
        )
        .agg(
            Value=(metric_column, "sum")
        )
        .reset_index()
    )


monthly_data["Category Display"] = (
    monthly_data["Category"]
    .apply(category_label)
)


# ============================================================
# COMPLETE MONTH RANGE
# ============================================================

all_months = pd.date_range(
    start=df["Month"].min(),
    end=df["Month"].max(),
    freq="MS"
)

all_categories = sorted(
    selected_category_codes
)


complete_index = pd.MultiIndex.from_product(
    [
        all_months,
        all_categories
    ],
    names=[
        "Month",
        "Category"
    ]
)


# Reindex without a global fill_value.
# Using fill_value=0 here attempts to put integer 0 into
# string/Arrow columns such as Category, which causes:
# TypeError: Invalid value '0' for dtype 'str'.
monthly_data = (
    monthly_data
    .set_index(["Month", "Category"])
    .reindex(complete_index)
    .reset_index()
)

# Fill only the numeric metric column.
monthly_data["Value"] = pd.to_numeric(
    monthly_data["Value"],
    errors="coerce"
).fillna(0)


monthly_data["Category Display"] = (
    monthly_data["Category"]
    .apply(category_label)
)


# ============================================================
# CATEGORY TOTALS
# ============================================================

category_totals = (
    monthly_data
    .groupby("Category Display")["Value"]
    .sum()
    .sort_values(
        ascending=False
    )
)


# Keep the selected top categories.
top_categories = (
    category_totals
    .head(max_categories)
    .index
    .tolist()
)


stream_data = monthly_data[
    monthly_data["Category Display"].isin(
        top_categories
    )
].copy()


# ============================================================
# PIVOT FOR STREAMGRAPH
# ============================================================

stream_pivot = (
    stream_data
    .pivot(
        index="Month",
        columns="Category Display",
        values="Value"
    )
)

# Ensure the streamgraph always receives numeric values.
stream_pivot = stream_pivot.apply(
    pd.to_numeric,
    errors="coerce"
).fillna(0)


# Sort categories by total contribution.
ordered_categories = (
    stream_pivot.sum()
    .sort_values(
        ascending=False
    )
    .index
    .tolist()
)


stream_pivot = stream_pivot[
    ordered_categories
]


# ============================================================
# KPI CARDS
# ============================================================

total_value = stream_data["Value"].sum()

active_categories = (
    stream_data[
        stream_data["Value"] > 0
    ]["Category Display"]
    .nunique()
)

latest_month = stream_pivot.index.max()

latest_month_total = (
    stream_pivot
    .loc[latest_month]
    .sum()
)


if len(stream_pivot) >= 2:

    previous_month_total = (
        stream_pivot
        .iloc[-2]
        .sum()
    )

    if previous_month_total != 0:

        latest_growth = (
            (
                latest_month_total
                - previous_month_total
            )
            / previous_month_total
        ) * 100

    else:

        latest_growth = None

else:

    latest_growth = None


col1, col2, col3, col4 = st.columns(4)


with col1:

    if metric == "App Count":

        st.metric(
            "Total App Records",
            f"{total_value:,.0f}"
        )

    else:

        st.metric(
            f"Total {metric}",
            f"{total_value:,.0f}"
        )


with col2:

    st.metric(
        "Categories Shown",
        f"{len(ordered_categories):,}"
    )


with col3:

    st.metric(
        "Latest Month",
        latest_month.strftime(
            "%b %Y"
        )
    )


with col4:

    if latest_growth is None:

        st.metric(
            "Latest MoM Growth",
            "N/A"
        )

    else:

        st.metric(
            "Latest MoM Growth",
            f"{latest_growth:+.2f}%"
        )


# ============================================================
# STREAMGRAPH
# ============================================================

st.subheader(
    "🌊 Category Streamgraph"
)

st.caption(
    f"Metric: **{metric}** | "
    f"Showing the top **{len(ordered_categories)}** categories "
    "by total contribution."
)


fig = go.Figure()


for category in ordered_categories:

    values = stream_pivot[
        category
    ].values

    fig.add_trace(
        go.Scatter(

            x=stream_pivot.index,

            y=values,

            mode="lines",

            name=category,

            stackgroup="one",

            groupnorm=None,

            line=dict(
                width=0.5
            ),

            hovertemplate=(
                "<b>Category:</b> "
                f"{category}"
                "<br>"
                "<b>Month:</b> "
                "%{x|%B %Y}"
                "<br>"
                f"<b>{metric}:</b> "
                "%{y:,.0f}"
                "<extra></extra>"
            )
        )
    )


fig.update_layout(

    height=650,

    hovermode="x unified",

    xaxis=dict(
        title="Month",
        showgrid=False
    ),

    yaxis=dict(
        title=metric,
        showgrid=True
    ),

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    ),

    margin=dict(
        l=20,
        r=20,
        t=70,
        b=30
    )
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# CATEGORY TREND TABLE
# ============================================================

st.subheader(
    "📊 Category Trend Summary"
)


summary = (
    stream_pivot
    .sum()
    .sort_values(
        ascending=False
    )
    .reset_index()
)


summary.columns = [
    "Category",
    f"Total {metric}"
]


# Add latest month value.
latest_values = (
    stream_pivot
    .iloc[-1]
    .reindex(
        summary["Category"]
    )
    .values
)


summary[
    f"Latest Month ({latest_month.strftime('%b %Y')})"
] = latest_values


# Add percentage share.
summary["Share %"] = (
    summary[f"Total {metric}"]
    / summary[f"Total {metric}"].sum()
    * 100
)


summary["Share %"] = (
    summary["Share %"]
    .round(2)
)


st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# MONTHLY TOTAL TREND
# ============================================================

st.subheader(
    "📈 Overall Monthly Trend"
)


monthly_total = (
    stream_pivot
    .sum(axis=1)
)


trend_fig = go.Figure()


trend_fig.add_trace(
    go.Scatter(

        x=monthly_total.index,

        y=monthly_total.values,

        mode="lines+markers",

        name="Total",

        hovertemplate=(
            "<b>Month:</b> "
            "%{x|%B %Y}"
            "<br>"
            f"<b>Total {metric}:</b> "
            "%{y:,.0f}"
            "<extra></extra>"
        )
    )
)


trend_fig.update_layout(

    height=400,

    xaxis_title="Month",

    yaxis_title=f"Total {metric}",

    hovermode="x unified"
)


st.plotly_chart(
    trend_fig,
    use_container_width=True
)


# ============================================================
# METHODOLOGY
# ============================================================

with st.expander(
    "ℹ️ Methodology"
):

    st.markdown(
        """
### Streamgraph

The streamgraph visualizes how different Google Play Store
categories contribute to the selected metric over time.

### Available Metrics

**App Count**
- Number of unique apps recorded for each category and month.

**Reviews**
- Sum of the `Reviews` column for each category and month.

**Install Lower Bound**
- Numeric lower bound extracted from the `Installs` column.
- For example, `10,000+` is represented as `10000`.

### Time Dimension

The `Last Updated` column is converted into monthly periods.

### Category Selection

Use the sidebar to select specific categories.

The **Maximum Categories** slider controls how many selected
categories are displayed in the streamgraph.

### Hover Information

Hover over any stream to see:

- Category
- Month
- Selected metric value

### Data Source

Google Play Store dataset:

`data/googleplaystore.csv`

### Access Restriction

This dashboard is available only between:

**6:00 PM – 9:00 PM IST**
        """
    )


# ============================================================
# FOOTER
# ============================================================

current_ist = datetime.now(IST)

st.caption(
    "Last refreshed: "
    + current_ist.strftime(
        "%d %b %Y, %I:%M:%S %p IST"
    )
)
