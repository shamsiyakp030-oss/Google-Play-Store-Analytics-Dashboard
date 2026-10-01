# ============================================================
# 6_Radar_Chart.py
# Google Play Store Analytics
# Category Performance Radar Chart
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Radar Chart | Google Play Store",
    page_icon="🎯",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 40px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }

    .sub-title {
        text-align: center;
        font-size: 17px;
        color: #777;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">🎯 Google Play Store Radar Analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Compare application category performance across multiple metrics'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# FIND DATASET
# ============================================================

CURRENT_DIR = Path(__file__).resolve().parent

PROJECT_ROOT = CURRENT_DIR.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "googleplaystore.csv"
)


# ============================================================
# CHECK DATASET
# ============================================================

if not DATA_FILE.exists():

    st.error(
        "❌ Could not find `googleplaystore.csv`."
    )

    st.warning(
        "Expected dataset location:"
    )

    st.code(
        str(DATA_FILE),
        language="text"
    )

    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data(file_path):

    try:

        data = pd.read_csv(
            file_path,
            encoding="utf-8",
            on_bad_lines="skip"
        )

    except UnicodeDecodeError:

        data = pd.read_csv(
            file_path,
            encoding="latin1",
            on_bad_lines="skip"
        )

    return data


try:

    df = load_data(str(DATA_FILE))

except Exception as e:

    st.error(
        f"❌ Error loading dataset: {e}"
    )

    st.stop()


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace(".", "_")
)


# ============================================================
# REMOVE DUPLICATES
# ============================================================

df = df.drop_duplicates()


# ============================================================
# DATA PREPROCESSING
# ============================================================

# ------------------------------------------------------------
# Rating
# ------------------------------------------------------------

if "rating" in df.columns:

    df["rating"] = pd.to_numeric(
        df["rating"],
        errors="coerce"
    )


# ------------------------------------------------------------
# Reviews
# ------------------------------------------------------------

if "reviews" in df.columns:

    df["reviews"] = (
        df["reviews"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    df["reviews"] = pd.to_numeric(
        df["reviews"],
        errors="coerce"
    )


# ------------------------------------------------------------
# Installs
# ------------------------------------------------------------

if "installs" in df.columns:

    df["installs"] = (
        df["installs"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("+", "", regex=False)
        .str.strip()
    )

    df["installs"] = pd.to_numeric(
        df["installs"],
        errors="coerce"
    )


# ------------------------------------------------------------
# Price
# ------------------------------------------------------------

if "price" in df.columns:

    df["price"] = (
        df["price"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    )


# ------------------------------------------------------------
# Size
# ------------------------------------------------------------

if "size" in df.columns:

    df["size"] = (
        df["size"]
        .astype(str)
        .str.replace("M", "", regex=False)
        .str.replace("k", "", regex=False)
        .str.strip()
    )

    df["size"] = pd.to_numeric(
        df["size"],
        errors="coerce"
    )


# ============================================================
# VALIDATE CATEGORY
# ============================================================

if "category" not in df.columns:

    st.error(
        "❌ `Category` column was not found in the dataset."
    )

    st.stop()


# ============================================================
# REMOVE INVALID RATINGS
# ============================================================

if "rating" in df.columns:

    df.loc[
        ~df["rating"].between(0, 5),
        "rating"
    ] = np.nan


# ============================================================
# DATASET OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">📊 Dataset Overview</div>',
    unsafe_allow_html=True
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Apps",
        f"{len(df):,}"
    )


with col2:

    st.metric(
        "Categories",
        df["category"].nunique()
    )


with col3:

    if "rating" in df.columns:

        st.metric(
            "Average Rating",
            f"{df['rating'].mean():.2f}"
        )

    else:

        st.metric(
            "Average Rating",
            "N/A"
        )


with col4:

    if "installs" in df.columns:

        st.metric(
            "Total Installs",
            f"{df['installs'].sum():,.0f}"
        )

    else:

        st.metric(
            "Total Installs",
            "N/A"
        )


# ============================================================
# AVAILABLE METRICS
# ============================================================

available_metrics = []

if "rating" in df.columns:
    available_metrics.append("rating")

if "reviews" in df.columns:
    available_metrics.append("reviews")

if "installs" in df.columns:
    available_metrics.append("installs")

if "price" in df.columns:
    available_metrics.append("price")

if "size" in df.columns:
    available_metrics.append("size")


# ============================================================
# FEATURE SELECTION
# ============================================================

st.markdown(
    '<div class="section-title">⚙️ Radar Metrics</div>',
    unsafe_allow_html=True
)


selected_metrics = st.multiselect(

    "Select metrics to compare:",

    options=available_metrics,

    default=[
        metric
        for metric in [
            "rating",
            "reviews",
            "installs",
            "price"
        ]
        if metric in available_metrics
    ]

)


if len(selected_metrics) < 3:

    st.warning(
        "⚠️ Please select at least 3 metrics "
        "for a meaningful radar chart."
    )

    st.stop()


# ============================================================
# CATEGORY SELECTION
# ============================================================

st.markdown(
    '<div class="section-title">📱 Select Categories</div>',
    unsafe_allow_html=True
)


category_counts = (
    df["category"]
    .value_counts()
)


available_categories = (
    category_counts.index
    .tolist()
)


default_categories = (
    available_categories[:3]
)


selected_categories = st.multiselect(

    "Choose categories to compare:",

    options=available_categories,

    default=default_categories

)


if len(selected_categories) < 1:

    st.warning(
        "⚠️ Please select at least one category."
    )

    st.stop()


# ============================================================
# CATEGORY AGGREGATION
# ============================================================

category_data = (

    df[
        df["category"].isin(
            selected_categories
        )
    ]

    .groupby("category")[selected_metrics]

    .mean()

)


# ============================================================
# HANDLE MISSING VALUES
# ============================================================

category_data = category_data.fillna(0)


# ============================================================
# NORMALIZE DATA
# ============================================================

# Min-Max normalization allows different metrics
# such as Rating, Reviews and Installs to be
# displayed on the same radar scale.

normalized_data = pd.DataFrame(
    index=category_data.index
)


for metric in selected_metrics:

    minimum = category_data[metric].min()

    maximum = category_data[metric].max()

    if maximum == minimum:

        normalized_data[metric] = 50.0

    else:

        normalized_data[metric] = (
            (
                category_data[metric] - minimum
            )
            /
            (
                maximum - minimum
            )
        ) * 100


# ============================================================
# RADAR CHART
# ============================================================

st.markdown(
    '<div class="section-title">🎯 Category Performance Radar</div>',
    unsafe_allow_html=True
)


fig = go.Figure()


# Add one radar trace for every selected category

for category in selected_categories:

    values = normalized_data.loc[
        category,
        selected_metrics
    ].tolist()

    values.append(
        values[0]
    )

    theta = selected_metrics.copy()

    theta.append(
        theta[0]
    )

    fig.add_trace(

        go.Scatterpolar(

            r=values,

            theta=theta,

            fill="toself",

            name=category,

            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "%{theta}: %{r:.1f}<br>"
                "<extra></extra>"
            )

        )

    )


# ============================================================
# RADAR LAYOUT
# ============================================================

fig.update_layout(

    polar=dict(

        radialaxis=dict(

            visible=True,

            range=[
                0,
                100
            ],

            tickvals=[
                0,
                20,
                40,
                60,
                80,
                100
            ],

            ticktext=[
                "0",
                "20",
                "40",
                "60",
                "80",
                "100"
            ]

        )

    ),

    title={
        "text": "Normalized Category Performance Comparison",
        "x": 0.5
    },

    height=700,

    showlegend=True,

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    )

)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# CATEGORY PERFORMANCE TABLE
# ============================================================

st.markdown(
    '<div class="section-title">📋 Category Performance</div>',
    unsafe_allow_html=True
)


display_table = category_data.copy()


for metric in selected_metrics:

    if metric == "rating":

        display_table[metric] = (
            display_table[metric]
            .round(2)
        )

    else:

        display_table[metric] = (
            display_table[metric]
            .round(2)
        )


st.dataframe(
    display_table,
    use_container_width=True
)


# ============================================================
# NORMALIZED PERFORMANCE TABLE
# ============================================================

with st.expander(
    "📊 View Normalized Radar Values"
):

    st.dataframe(
        normalized_data.round(2),
        use_container_width=True
    )


# ============================================================
# CATEGORY APP COUNT
# ============================================================

st.markdown(
    '<div class="section-title">📱 Applications by Selected Category</div>',
    unsafe_allow_html=True
)


selected_category_counts = (

    df[
        df["category"].isin(
            selected_categories
        )
    ]

    ["category"]

    .value_counts()

    .sort_values(
        ascending=False
    )

    .reset_index()

)


selected_category_counts.columns = [
    "Category",
    "App Count"
]


st.dataframe(
    selected_category_counts,
    use_container_width=True
)


# ============================================================
# INSIGHTS
# ============================================================

st.markdown(
    '<div class="section-title">💡 Key Insights</div>',
    unsafe_allow_html=True
)


# Highest normalized overall category

overall_scores = (
    normalized_data
    .mean(axis=1)
    .sort_values(
        ascending=False
    )
)


top_category = (
    overall_scores.index[0]
)


top_score = (
    overall_scores.iloc[0]
)


st.info(

    f"📌 **Highest Overall Normalized Performance:** "
    f"**{top_category}** with a combined normalized "
    f"score of **{top_score:.1f}/100** across the selected metrics."

)


# Highest rating

if "rating" in selected_metrics:

    rating_category = (
        category_data["rating"]
        .idxmax()
    )

    rating_value = (
        category_data["rating"]
        .max()
    )

    st.info(

        f"⭐ **Highest Average Rating:** "
        f"**{rating_category}** "
        f"({rating_value:.2f}/5)."

    )


# Highest reviews

if "reviews" in selected_metrics:

    review_category = (
        category_data["reviews"]
        .idxmax()
    )

    st.info(

        f"💬 **Highest Average Reviews:** "
        f"**{review_category}** has the highest "
        f"average number of reviews."

    )


# Highest installs

if "installs" in selected_metrics:

    install_category = (
        category_data["installs"]
        .idxmax()
    )

    st.info(

        f"📥 **Highest Average Installs:** "
        f"**{install_category}** has the highest "
        f"average install value among the selected categories."

    )


# ============================================================
# EXPLANATION
# ============================================================

with st.expander(
    "ℹ️ How to Interpret the Radar Chart"
):

    st.markdown(
        """
        ### Radar Chart Interpretation

        The radar chart compares selected Google Play Store
        categories across multiple performance metrics.

        **Important:** Because Rating, Reviews, Installs,
        Price and Size have very different scales, the values
        are normalized from **0 to 100** before creating the
        radar chart.

        - **100** → Highest value among the selected categories
        - **0** → Lowest value among the selected categories
        - Larger area → Relatively stronger performance across
          the selected metrics
        - Smaller area → Relatively lower performance across
          the selected metrics

        This visualization helps identify differences in
        application-category performance.
        """
    )


# ============================================================
# DOWNLOAD DATA
# ============================================================

st.markdown(
    '<div class="section-title">⬇️ Download Results</div>',
    unsafe_allow_html=True
)


download_data = category_data.to_csv()


st.download_button(

    label="📥 Download Category Analysis",

    data=download_data,

    file_name="googleplaystore_radar_analysis.csv",

    mime="text/csv"

)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:gray;">

    <b>Google Play Store Analytics Dashboard</b><br>

    Radar Chart • Category Performance Analysis<br>

    Built with Python, Pandas, Plotly & Streamlit

    </div>
    """,
    unsafe_allow_html=True
)