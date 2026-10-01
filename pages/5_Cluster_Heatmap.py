# ============================================================
# 5_Cluster_Heatmap.py
# Google Play Store Analytics
# K-Means Clustering + Cluster Heatmap
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Cluster Heatmap | Google Play Store",
    page_icon="🔥",
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
    '<div class="main-title">🔥 Google Play Store Cluster Heatmap</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'K-Means clustering and heatmap analysis of Google Play Store applications'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# FIND DATASET AUTOMATICALLY
# ============================================================

from pathlib import Path

# Current file location:
# .../Google_Play_Analytics_Internship_Project/pages/
CURRENT_DIR = Path(__file__).resolve().parent

# Project root:
# .../Google_Play_Analytics_Internship_Project/
PROJECT_ROOT = CURRENT_DIR.parent

# Dataset location:
DATA_FILE = PROJECT_ROOT / "data" / "googleplaystore.csv"


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
# IF DATASET NOT FOUND
# ============================================================

if DATA_FILE is None:

    st.error(
        "❌ Could not find `googleplaystore.csv`."
    )

    st.warning(
        "Please place the CSV file in the same folder as "
        "`5_Cluster_Heatmap.py`."
    )

    st.info(
        f"Streamlit is currently looking in:\n\n"
        f"`{CURRENT_DIR}`"
    )

    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data(file_path):

    df = pd.read_csv(
        file_path,
        encoding="utf-8",
        on_bad_lines="skip"
    )

    return df


try:

    df = load_data(str(DATA_FILE))

except UnicodeDecodeError:

    try:

        df = pd.read_csv(
            str(DATA_FILE),
            encoding="latin1",
            on_bad_lines="skip"
        )

    except Exception as e:

        st.error(
            f"❌ Could not read the CSV file: {e}"
        )

        st.stop()

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
# REMOVE DUPLICATE ROWS
# ============================================================

df = df.drop_duplicates()


# ============================================================
# DATA PREPROCESSING
# ============================================================

# -------------------------------
# Rating
# -------------------------------

if "rating" in df.columns:

    df["rating"] = pd.to_numeric(
        df["rating"],
        errors="coerce"
    )


# -------------------------------
# Reviews
# -------------------------------

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


# -------------------------------
# Installs
# -------------------------------

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


# -------------------------------
# Price
# -------------------------------

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


# -------------------------------
# Size
# -------------------------------

if "size" in df.columns:

    size_values = (
        df["size"]
        .astype(str)
        .str.strip()
    )

    df["size"] = (
        size_values
        .str.replace("M", "", regex=False)
        .str.replace("k", "", regex=False)
    )

    df["size"] = pd.to_numeric(
        df["size"],
        errors="coerce"
    )


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
        "Total Columns",
        len(df.columns)
    )


with col3:

    if "category" in df.columns:

        st.metric(
            "Categories",
            df["category"].nunique()
        )

    else:

        st.metric(
            "Categories",
            "N/A"
        )


with col4:

    if "rating" in df.columns:

        avg_rating = df["rating"].mean()

        st.metric(
            "Average Rating",
            f"{avg_rating:.2f}"
        )

    else:

        st.metric(
            "Average Rating",
            "N/A"
        )


# ============================================================
# DATASET INFORMATION
# ============================================================

with st.expander("📁 Dataset Information"):

    st.write(
        f"**Dataset file:** `{DATA_FILE.name}`"
    )

    st.write(
        f"**Rows:** {len(df):,}"
    )

    st.write(
        f"**Columns:** {len(df.columns)}"
    )

    st.dataframe(
        df.head(10),
        use_container_width=True
    )


# ============================================================
# AVAILABLE CLUSTERING FEATURES
# ============================================================

available_features = [

    column

    for column in [

        "rating",
        "reviews",
        "size",
        "installs",
        "price"

    ]

    if column in df.columns

]


# ============================================================
# CHECK FEATURES
# ============================================================

if len(available_features) < 2:

    st.error(
        "❌ At least two numerical features are required "
        "for clustering."
    )

    st.write(
        "Available columns:"
    )

    st.write(
        df.columns.tolist()
    )

    st.stop()


# ============================================================
# FEATURE SELECTION
# ============================================================

st.markdown(
    '<div class="section-title">⚙️ Select Clustering Features</div>',
    unsafe_allow_html=True
)


default_features = available_features[
    :min(4, len(available_features))
]


selected_features = st.multiselect(

    "Choose numerical features for clustering:",

    options=available_features,

    default=default_features

)


if len(selected_features) < 2:

    st.warning(
        "⚠️ Please select at least two features."
    )

    st.stop()


# ============================================================
# PREPARE CLUSTER DATA
# ============================================================

cluster_df = df[
    selected_features
].copy()


# Replace infinity values

cluster_df = cluster_df.replace(
    [np.inf, -np.inf],
    np.nan
)


# Remove missing values

cluster_df = cluster_df.dropna()


# ============================================================
# CHECK DATA SIZE
# ============================================================

if len(cluster_df) < 10:

    st.error(
        "❌ Not enough valid data points available "
        "for clustering."
    )

    st.stop()


# ============================================================
# REMOVE EXTREME OUTLIERS
# ============================================================

for column in selected_features:

    lower_limit = cluster_df[
        column
    ].quantile(0.01)

    upper_limit = cluster_df[
        column
    ].quantile(0.99)

    cluster_df[column] = cluster_df[
        column
    ].clip(
        lower_limit,
        upper_limit
    )


# ============================================================
# STANDARDIZATION
# ============================================================

scaler = StandardScaler()


scaled_data = scaler.fit_transform(
    cluster_df[selected_features]
)


# ============================================================
# CLUSTER CONFIGURATION
# ============================================================

st.markdown(
    '<div class="section-title">🎯 Clustering Configuration</div>',
    unsafe_allow_html=True
)


col1, col2 = st.columns(2)


with col1:

    n_clusters = st.slider(

        "Number of Clusters (K)",

        min_value=2,

        max_value=8,

        value=4,

        step=1

    )


with col2:

    st.metric(
        "Apps Used for Clustering",
        f"{len(cluster_df):,}"
    )


# ============================================================
# K-MEANS CLUSTERING
# ============================================================

kmeans = KMeans(

    n_clusters=n_clusters,

    random_state=42,

    n_init=10

)


cluster_labels = kmeans.fit_predict(
    scaled_data
)


cluster_df["Cluster"] = cluster_labels


# ============================================================
# CLUSTER SUMMARY
# ============================================================

st.markdown(
    '<div class="section-title">📋 Cluster Summary</div>',
    unsafe_allow_html=True
)


cluster_summary = (

    cluster_df

    .groupby("Cluster")[selected_features]

    .mean()

    .round(2)

)


cluster_counts = (

    cluster_df["Cluster"]

    .value_counts()

    .sort_index()

)


cluster_summary.insert(
    0,
    "App Count",
    cluster_counts
)


st.dataframe(
    cluster_summary,
    use_container_width=True
)


# ============================================================
# HEATMAP
# ============================================================

st.markdown(
    '<div class="section-title">🔥 Cluster Heatmap</div>',
    unsafe_allow_html=True
)


# Calculate average values

heatmap_data = (

    cluster_df

    .groupby("Cluster")[selected_features]

    .mean()

)


# Standardize cluster means

heatmap_scaled = pd.DataFrame(

    StandardScaler().fit_transform(
        heatmap_data
    ),

    index=heatmap_data.index,

    columns=heatmap_data.columns

)


# Create heatmap

fig_heatmap = px.imshow(

    heatmap_scaled,

    text_auto=".2f",

    aspect="auto",

    labels={
        "x": "Features",
        "y": "Cluster",
        "color": "Standardized Value"
    },

    title="Cluster Characteristics Heatmap"

)


fig_heatmap.update_layout(
    height=550
)


st.plotly_chart(
    fig_heatmap,
    use_container_width=True
)


# ============================================================
# CLUSTER DISTRIBUTION
# ============================================================

st.markdown(
    '<div class="section-title">📊 Cluster Distribution</div>',
    unsafe_allow_html=True
)


distribution_df = (

    cluster_df["Cluster"]

    .value_counts()

    .sort_index()

    .reset_index()

)


distribution_df.columns = [
    "Cluster",
    "App Count"
]


fig_distribution = px.bar(

    distribution_df,

    x="Cluster",

    y="App Count",

    text="App Count",

    title="Number of Apps in Each Cluster"

)


fig_distribution.update_traces(
    textposition="outside"
)


fig_distribution.update_layout(
    height=450
)


st.plotly_chart(
    fig_distribution,
    use_container_width=True
)


# ============================================================
# SCATTER PLOT
# ============================================================

st.markdown(
    '<div class="section-title">🔍 Cluster Visualization</div>',
    unsafe_allow_html=True
)


col1, col2 = st.columns(2)


with col1:

    x_feature = st.selectbox(

        "X-axis Feature",

        selected_features,

        index=0

    )


with col2:

    y_feature = st.selectbox(

        "Y-axis Feature",

        selected_features,

        index=min(
            1,
            len(selected_features) - 1
        )

    )


scatter_fig = px.scatter(

    cluster_df,

    x=x_feature,

    y=y_feature,

    color="Cluster",

    hover_data=selected_features,

    title=(
        f"Cluster Visualization: "
        f"{x_feature} vs {y_feature}"
    )

)


scatter_fig.update_layout(
    height=550
)


st.plotly_chart(
    scatter_fig,
    use_container_width=True
)


# ============================================================
# CLUSTER INSIGHTS
# ============================================================

st.markdown(
    '<div class="section-title">💡 Key Insights</div>',
    unsafe_allow_html=True
)


# Largest cluster

largest_cluster = (
    cluster_counts.idxmax()
)


largest_cluster_count = (
    cluster_counts.max()
)


st.info(

    f"📌 **Largest Cluster:** "
    f"Cluster {largest_cluster} contains "
    f"**{largest_cluster_count:,} apps**."

)


# Highest rating cluster

if "rating" in selected_features:

    highest_rating_cluster = (
        heatmap_data["rating"].idxmax()
    )

    highest_rating = (
        heatmap_data["rating"].max()
    )

    st.info(

        f"⭐ **Highest Average Rating:** "
        f"Cluster {highest_rating_cluster} "
        f"has an average rating of "
        f"**{highest_rating:.2f}**."

    )


# Highest installs cluster

if "installs" in selected_features:

    highest_install_cluster = (
        heatmap_data["installs"].idxmax()
    )

    highest_install_value = (
        heatmap_data["installs"].max()
    )

    st.info(

        f"📱 **Highest Average Installs:** "
        f"Cluster {highest_install_cluster} "
        f"has the highest average install value "
        f"among the clusters."

    )


# Highest review cluster

if "reviews" in selected_features:

    highest_review_cluster = (
        heatmap_data["reviews"].idxmax()
    )

    st.info(

        f"💬 **Highest Average Reviews:** "
        f"Cluster {highest_review_cluster} "
        f"has the highest average number of reviews."

    )


st.info(

    "📊 **Heatmap Interpretation:** "
    "Positive standardized values indicate that a cluster "
    "has relatively higher values for a feature, while "
    "negative values indicate relatively lower values."

)


st.info(

    "⚙️ **Methodology:** "
    "The numerical features are standardized before applying "
    "K-Means so that features with different scales can "
    "contribute more comparably to the clustering process."

)


# ============================================================
# DOWNLOAD CLUSTERED DATA
# ============================================================

st.markdown(
    '<div class="section-title">⬇️ Download Results</div>',
    unsafe_allow_html=True
)


download_data = cluster_df.to_csv(
    index=False
)


st.download_button(

    label="📥 Download Clustered Dataset",

    data=download_data,

    file_name="googleplaystore_clustered.csv",

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

    Cluster Heatmap • K-Means Clustering • Data Visualization<br>

    Built with Python, Pandas, Scikit-Learn, Streamlit & Plotly

    </div>
    """,

    unsafe_allow_html=True

)