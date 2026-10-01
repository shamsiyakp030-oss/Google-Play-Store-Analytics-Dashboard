import streamlit as st
import pandas as pd
import plotly.express as px

from utils.cleaning import load_data
from utils.time_control import check_time


# -----------------------------------
# Page Configuration
# -----------------------------------

st.set_page_config(
    page_title="Hexbin Density Analysis",
    layout="wide"
)


st.title(
    "📊 App Size vs Rating - Hexbin Density Analysis"
)


# -----------------------------------
# Time Restriction
# 5 PM - 7 PM IST
# -----------------------------------

if not check_time(17, 19):

    st.warning(
        "This visualization is available only between 5 PM and 7 PM IST"
    )

    st.stop()



# -----------------------------------
# Load Dataset
# -----------------------------------

df = load_data()



# -----------------------------------
# IQR Outlier Detection Function
# -----------------------------------

def detect_category_outliers(data):

    outliers = []

    for category in data["Category"].unique():

        temp = data[
            data["Category"] == category
        ]


        Q1 = temp["Installs"].quantile(0.25)

        Q3 = temp["Installs"].quantile(0.75)


        IQR = Q3 - Q1


        lower_limit = Q1 - (1.5 * IQR)

        upper_limit = Q3 + (1.5 * IQR)


        category_outliers = temp[
            (temp["Installs"] < lower_limit)
            |
            (temp["Installs"] > upper_limit)
        ]


        outliers.append(
            category_outliers
        )


    if len(outliers) > 0:
        return pd.concat(outliers)

    else:
        return pd.DataFrame()



# -----------------------------------
# Category Selection
# -----------------------------------

categories = [

    "GAME",
    "BEAUTY",
    "BUSINESS",
    "COMICS",
    "COMMUNICATION",
    "DATING",
    "ENTERTAINMENT",
    "SOCIAL",
    "EVENTS"

]


df = df[
    df["Category"]
    .isin(categories)
]



# -----------------------------------
# Apply Filters
# -----------------------------------

df = df[
    df["Rating"] > 3.5
]


df = df[
    df["Installs"] > 50000
]


df = df[
    df["Reviews"] > 500
]


df = df[
    df["Size"]
    .between(10,100)
]



# -----------------------------------
# Remove Apps containing S/s
# -----------------------------------

df = df[
    ~df["App"]
    .str.contains(
        "s",
        case=False,
        na=False
    )
]



# -----------------------------------
# Category Translation
# -----------------------------------

translation = {

    "BEAUTY":"सौंदर्य",

    "BUSINESS":"வணிகம்",

    "DATING":"Verabredung"

}


df["Category_Translated"] = (
    df["Category"]
    .replace(translation)
)



# -----------------------------------
# Detect Outliers
# -----------------------------------

outlier_df = detect_category_outliers(df)



# -----------------------------------
# Dataset Preview
# -----------------------------------

st.subheader(
    "Filtered Dataset"
)


st.dataframe(
    df.head(20)
)



# -----------------------------------
# Hexbin Density Chart
# -----------------------------------

fig = px.density_heatmap(

    df,

    x="Size",

    y="Rating",

    z="Installs",

    histfunc="avg",

    nbinsx=30,

    nbinsy=30,

    marginal_x="histogram",

    marginal_y="histogram",

    title=
    "Average Installs Density by App Size and Rating"

)



# -----------------------------------
# Add Outlier Labels
# -----------------------------------

if not outlier_df.empty:


    fig.add_scatter(

        x=outlier_df["Size"],

        y=outlier_df["Rating"],

        mode="markers+text",

        text=outlier_df["App"],

        textposition="top center",

        marker=dict(

            size=12,

            color="red"

        ),

        name="IQR Outliers"

    )



# -----------------------------------
# Highlight Game Apps Pink
# -----------------------------------

game_df = df[
    df["Category"]=="GAME"
]


fig.add_scatter(

    x=game_df["Size"],

    y=game_df["Rating"],

    mode="markers",

    marker=dict(

        size=10,

        color="pink"

    ),

    name="Game Apps"

)



# -----------------------------------
# Layout
# -----------------------------------

fig.update_layout(

    height=750,

    hovermode="closest"

)



# -----------------------------------
# Display Chart
# -----------------------------------

st.plotly_chart(

    fig,

    use_container_width=True

)



# -----------------------------------
# Insights
# -----------------------------------

st.subheader(
    "Key Information"
)


col1,col2,col3 = st.columns(3)


with col1:

    st.metric(
        "Filtered Apps",
        len(df)
    )


with col2:

    st.metric(
        "Average Rating",
        round(df["Rating"].mean(),2)
    )


with col3:

    st.metric(
        "Average Installs",
        int(df["Installs"].mean())
    )