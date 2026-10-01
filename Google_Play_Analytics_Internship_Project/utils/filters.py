import pandas as pd


# -----------------------------
# Filter by Rating
# -----------------------------

def rating_filter(df, minimum_rating):

    return df[
        df["Rating"] >= minimum_rating
    ]



# -----------------------------
# Filter by Installs
# -----------------------------

def installs_filter(df, minimum_installs):

    return df[
        df["Installs"] >= minimum_installs
    ]



# -----------------------------
# Filter by Reviews
# -----------------------------

def reviews_filter(df, minimum_reviews):

    return df[
        df["Reviews"] >= minimum_reviews
    ]



# -----------------------------
# Filter by Size
# -----------------------------

def size_filter(df, min_size, max_size):

    return df[
        df["Size"].between(
            min_size,
            max_size
        )
    ]



# -----------------------------
# Remove App Names
# containing letters/numbers
# -----------------------------

def exclude_app_names(df, letters):

    pattern = "|".join(letters)

    return df[
        ~df["App"]
        .str.contains(
            pattern,
            case=False,
            na=False
        )
    ]



# -----------------------------
# Category Filter
# -----------------------------

def category_filter(df, categories):

    return df[
        df["Category"]
        .isin(categories)
    ]