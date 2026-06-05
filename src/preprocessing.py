import pandas as pd


def filter_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.dropna(subset=["price", "price_per_m2"])

    df = df.drop_duplicates(subset="id")

    df = df[
        (df["price"] > 1_000_000) &
        (df["area"] >= 10) &
        (df["area"] <= 400) &
        (df["rooms"] >= 1) &
        (df["rooms"] <= 10) &
        (df["total_floors"] <= 50)
    ]

    return df


def fill_categorical_missing(
    df: pd.DataFrame,
    cat_features: list[str]
) -> pd.DataFrame:
    df = df.copy()

    for col in cat_features:
        if col in df.columns:
            df[col] = df[col].fillna("unknown").astype(str)

    return df


def fill_numeric_missing(
    df: pd.DataFrame,
    numeric_features: list[str]
) -> pd.DataFrame:
    df = df.copy()

    for col in numeric_features:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    return df


def preprocess_data(
    df: pd.DataFrame,
    features: list[str],
    cat_features: list[str]
) -> pd.DataFrame:
    df = df.copy()

    df = filter_invalid_rows(df)

    df = fill_categorical_missing(df, cat_features)

    numeric_features = [
        col for col in features
        if col not in cat_features
    ]

    df = fill_numeric_missing(df, numeric_features)

    return df