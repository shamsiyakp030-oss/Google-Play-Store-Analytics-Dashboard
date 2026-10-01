# ============================================================
# 3_Calendar_Heatmap.py
# Google Play Store Calendar Heatmap & Forecast Dashboard
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
    page_title="Calendar Heatmap Analytics",
    page_icon="📅",
    layout="wide",
)


# ============================================================
# PROJECT / DATA PATH
# ============================================================

# This file is inside:
# Project/pages/3_Calendar_Heatmap.py
#
# Dataset is inside:
# Project/data/googleplaystore.csv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "googleplaystore.csv"


# ============================================================
# IST TIME RESTRICTION
# 6:00 PM - 9:00 PM IST
# ============================================================

IST = ZoneInfo("Asia/Kolkata")

ACCESS_START = time(18, 0)   # 6:00 PM
ACCESS_END = time(21, 0)     # 9:00 PM


def access_allowed():
    current_time = datetime.now(IST).time()
    return ACCESS_START <= current_time < ACCESS_END


if not access_allowed():

    current_time = datetime.now(IST)

    st.title("📅 Calendar Heatmap Analytics")

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
        col for col in required_columns
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

    # --------------------------------------------------------
    # Remove duplicate records
    # --------------------------------------------------------

    df = df.drop_duplicates(
        subset=[
            "App",
            "Category",
            "Last Updated"
        ]
    )

    # --------------------------------------------------------
    # Date features
    # --------------------------------------------------------

    df["Date"] = df["Last Updated"].dt.normalize()

    df["Month"] = (
        df["Last Updated"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    # --------------------------------------------------------
    # Category display
    # --------------------------------------------------------

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
        "    └── 3_Calendar_Heatmap.py"
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
    '📅 Google Play Calendar Analytics'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Calendar activity, category analysis, '
    'month-over-month growth and 3-month forecasting'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🎛️ Dashboard Controls")

    categories = sorted(
        df["Category"].dropna().unique()
    )

    category_options = [
        "All Categories"
    ] + list(categories)

    selected_category = st.selectbox(
        "Select Category",
        category_options,
        format_func=lambda x:
            "All Categories"
            if x == "All Categories"
            else category_label(x)
    )

    metric = st.selectbox(
        "Select Metric",
        [
            "App Updates",
            "Reviews",
            "Install Lower Bound"
        ]
    )

    st.divider()

    st.write(
        "**Dataset Information**"
    )

    st.caption(
        f"Rows: {len(df):,}"
    )

    st.caption(
        f"Start: "
        f"{df['Date'].min().strftime('%d %b %Y')}"
    )

    st.caption(
        f"End: "
        f"{df['Date'].max().strftime('%d %b %Y')}"
    )

    st.caption(
        "Access: 6 PM – 9 PM IST"
    )


# ============================================================
# FILTER CATEGORY
# ============================================================

if selected_category == "All Categories":

    filtered_df = df.copy()

else:

    filtered_df = df[
        df["Category"] == selected_category
    ].copy()


if filtered_df.empty:

    st.warning(
        "No data available for the selected category."
    )

    st.stop()


# ============================================================
# METRIC MAPPING
# ============================================================

metric_mapping = {

    "App Updates": "Apps",

    "Reviews": "Reviews",

    "Install Lower Bound": "Installs"

}


metric_column = metric_mapping[metric]


# ============================================================
# DAILY DATA
# ============================================================

daily = (
    filtered_df
    .groupby("Date")
    .agg(
        Apps=("App", "nunique"),
        Reviews=("Reviews", "sum"),
        Installs=("Install Count", "sum")
    )
    .sort_index()
)

daily = daily.asfreq(
    "D",
    fill_value=0
)

daily["Metric Value"] = (
    daily[metric_column]
    .fillna(0)
)


# ============================================================
# MONTHLY DATA
# ============================================================

monthly = (
    filtered_df
    .groupby("Month")
    .agg(
        Apps=("App", "nunique"),
        Reviews=("Reviews", "sum"),
        Installs=("Install Count", "sum")
    )
    .sort_index()
)

monthly = monthly.asfreq(
    "MS",
    fill_value=0
)

monthly["Metric Value"] = (
    monthly[metric_column]
    .fillna(0)
)


# ============================================================
# KPI
# ============================================================

total_apps = filtered_df["App"].nunique()

total_reviews = filtered_df["Reviews"].sum()

total_installs = filtered_df["Install Count"].sum()


if len(monthly) >= 2:

    current_value = monthly[
        "Metric Value"
    ].iloc[-1]

    previous_value = monthly[
        "Metric Value"
    ].iloc[-2]

    if previous_value != 0:

        latest_growth = (
            (current_value - previous_value)
            / previous_value
        ) * 100

    else:

        latest_growth = None

else:

    latest_growth = None


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Unique Apps",
        f"{total_apps:,.0f}"
    )


with col2:

    st.metric(
        "Total Reviews",
        f"{total_reviews:,.0f}"
    )


with col3:

    st.metric(
        "Install Lower Bound",
        f"{total_installs:,.0f}"
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
# CALENDAR HEATMAP
# ============================================================

st.subheader("🗓️ Calendar Heatmap")

calendar_df = daily[
    ["Metric Value"]
].copy()

calendar_df["Week"] = (
    calendar_df.index
    .to_period("W-SUN")
    .start_time
)

calendar_df["Weekday"] = (
    calendar_df.index.weekday
)

calendar_pivot = (
    calendar_df
    .pivot_table(
        index="Weekday",
        columns="Week",
        values="Metric Value",
        aggfunc="sum"
    )
)

calendar_pivot = calendar_pivot.reindex(
    range(7)
)

weekday_names = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]


heatmap = go.Figure(
    data=go.Heatmap(

        z=calendar_pivot.values,

        x=calendar_pivot.columns,

        y=weekday_names,

        colorscale="Viridis",

        xgap=2,

        ygap=2,

        colorbar=dict(
            title=metric
        ),

        hovertemplate=(
            "<b>Week:</b> "
            "%{x|%d %b %Y}"
            "<br>"
            "<b>Day:</b> %{y}"
            "<br>"
            f"<b>{metric}:</b> "
            "%{z:,.0f}"
            "<extra></extra>"
        )
    )
)


heatmap.update_layout(

    height=400,

    xaxis_title="Week",

    yaxis_title="Day",

    margin=dict(
        l=20,
        r=20,
        t=20,
        b=20
    )
)


st.plotly_chart(
    heatmap,
    use_container_width=True
)


# ============================================================
# MONTH OVER MONTH GROWTH
# ============================================================

st.subheader(
    "📈 Month-over-Month Growth"
)

mom = monthly[
    ["Metric Value"]
].copy()

mom["MoM Growth %"] = (
    mom["Metric Value"]
    .pct_change()
    * 100
)


mom_chart = go.Figure()


mom_chart.add_trace(
    go.Bar(

        x=mom.index,

        y=mom["MoM Growth %"],

        customdata=mom[
            "Metric Value"
        ],

        name="MoM Growth",

        hovertemplate=(
            "<b>Month:</b> "
            "%{x|%B %Y}"
            "<br>"
            "<b>Growth:</b> "
            "%{y:.2f}%"
            "<br>"
            f"<b>{metric}:</b> "
            "%{customdata:,.0f}"
            "<extra></extra>"
        )
    )
)


mom_chart.add_hline(
    y=0,
    line_width=1
)


mom_chart.update_layout(

    height=400,

    xaxis_title="Month",

    yaxis_title="Growth (%)",

    hovermode="x unified"
)


st.plotly_chart(
    mom_chart,
    use_container_width=True
)


# ============================================================
# 3-MONTH MOVING AVERAGE FORECAST
# ============================================================

st.subheader(
    "🔮 3-Month Moving-Average Forecast"
)


actual = (
    monthly["Metric Value"]
    .astype(float)
)


forecast = pd.Series(
    dtype=float
)


if len(actual) >= 3:

    history = actual.tolist()

    forecast_values = []

    for _ in range(3):

        next_value = (
            sum(history[-3:]) / 3
        )

        forecast_values.append(
            next_value
        )

        history.append(
            next_value
        )

    forecast_dates = pd.date_range(

        start=(
            actual.index[-1]
            + pd.offsets.MonthBegin(1)
        ),

        periods=3,

        freq="MS"
    )

    forecast = pd.Series(

        forecast_values,

        index=forecast_dates,

        name="Forecast"
    )

else:

    st.warning(
        "At least 3 months of data are required "
        "for the forecast."
    )


# ============================================================
# FORECAST VS ACTUAL
# ============================================================

forecast_chart = go.Figure()


forecast_chart.add_trace(
    go.Scatter(

        x=actual.index,

        y=actual.values,

        mode="lines+markers",

        name="Actual",

        hovertemplate=(
            "<b>Month:</b> "
            "%{x|%B %Y}"
            "<br>"
            "<b>Actual:</b> "
            "%{y:,.0f}"
            "<extra></extra>"
        )
    )
)


if not forecast.empty:

    forecast_chart.add_trace(
        go.Scatter(

            x=forecast.index,

            y=forecast.values,

            mode="lines+markers",

            name="3-Month MA Forecast",

            line=dict(
                dash="dash"
            ),

            hovertemplate=(
                "<b>Month:</b> "
                "%{x|%B %Y}"
                "<br>"
                "<b>Forecast:</b> "
                "%{y:,.0f}"
                "<br>"
                "<b>Method:</b> "
                "3-Month Moving Average"
                "<extra></extra>"
            )
        )
    )


forecast_chart.update_layout(

    height=450,

    xaxis_title="Month",

    yaxis_title=metric,

    hovermode="x unified"
)


st.plotly_chart(
    forecast_chart,
    use_container_width=True
)


# ============================================================
# FORECAST TABLE
# ============================================================

if not forecast.empty:

    st.subheader(
        "📊 Forecast Values"
    )

    forecast_table = pd.DataFrame({

        "Month":
            forecast.index.strftime(
                "%B %Y"
            ),

        "Forecast":
            forecast.values.round(2)

    })


    st.dataframe(

        forecast_table,

        use_container_width=True,

        hide_index=True
    )


# ============================================================
# CATEGORY SUMMARY
# ============================================================

st.subheader(
    "🏷️ Category Summary"
)


category_summary = (
    df
    .groupby("Category")
    .agg(

        Apps=("App", "nunique"),

        Reviews=("Reviews", "sum"),

        Installs=("Install Count", "sum")

    )
    .sort_values(
        "Apps",
        ascending=False
    )
)


category_summary[
    "Category"
] = category_summary.index.map(
    category_label
)


category_summary = (
    category_summary[
        [
            "Category",
            "Apps",
            "Reviews",
            "Installs"
        ]
    ]
    .reset_index(drop=True)
)


st.dataframe(

    category_summary,

    use_container_width=True,

    hide_index=True
)


# ============================================================
# METHODOLOGY
# ============================================================

with st.expander(
    "ℹ️ Methodology"
):

    st.markdown(
        """
### Calendar Heatmap

The calendar heatmap uses the **`Last Updated`** column
from the Google Play Store dataset.

### Month-over-Month Growth

Monthly growth is calculated using:

**Current Month − Previous Month / Previous Month × 100**

### 3-Month Moving Average

The forecast uses the most recent three monthly values.
The next three months are generated recursively using
the three-month moving average.

### Metrics

**App Updates**
- Number of unique apps recorded for the date/month.

**Reviews**
- Sum of the `Reviews` column.

**Install Lower Bound**
- Numeric lower bound extracted from values such as
  `1,000+`, `10,000+`, etc.

### Category Translation

Dataset category codes such as:

`ART_AND_DESIGN`

are displayed as:

`Art & Design`

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