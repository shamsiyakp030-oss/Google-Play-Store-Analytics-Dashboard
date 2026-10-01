import pandas as pd


def load_data():

    file_path = "data/googleplaystore.csv"

    df = pd.read_csv(file_path)

    df = clean_data(df)

    return df



def clean_data(df):

    # Remove duplicate rows
    df = df.drop_duplicates()


    # --------------------
    # Rating Cleaning
    # --------------------

    df["Rating"] = pd.to_numeric(
        df["Rating"],
        errors="coerce"
    )


    # --------------------
    # Reviews Cleaning
    # --------------------

    df["Reviews"] = pd.to_numeric(
        df["Reviews"],
        errors="coerce"
    )


    # --------------------
    # Installs Cleaning
    # --------------------

    df["Installs"] = (
        df["Installs"]
        .astype(str)
        .str.replace("+","")
        .str.replace(",","")
    )


    df["Installs"] = pd.to_numeric(
        df["Installs"],
        errors="coerce"
    )


    # --------------------
    # Size Cleaning
    # --------------------

    df["Size"] = (
        df["Size"]
        .astype(str)
        .str.replace("M","")
    )


    df["Size"] = pd.to_numeric(
        df["Size"],
        errors="coerce"
    )


    # --------------------
    # Price Cleaning
    # --------------------

    df["Price"] = (
        df["Price"]
        .astype(str)
        .str.replace("$","")
    )


    df["Price"] = pd.to_numeric(
        df["Price"],
        errors="coerce"
    )


    # Remove missing values

    df = df.dropna(
        subset=[
            "Rating",
            "Reviews",
            "Installs",
            "Size"
        ]
    )


    return df
