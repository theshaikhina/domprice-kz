import pandas as pd


def add_house_age(df: pd.DataFrame, current_year: int = 2026) -> pd.DataFrame:
    df = df.copy()

    if "house_age" not in df.columns and "year_built" in df.columns:
        df["house_age"] = current_year - df["year_built"]

    return df


def add_floor_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "floor_ratio" not in df.columns:
        df["floor_ratio"] = df["floor"] / df["total_floors"]

    if "is_first_floor" not in df.columns:
        df["is_first_floor"] = (df["floor"] == 1).astype(int)

    if "is_last_floor" not in df.columns:
        df["is_last_floor"] = (
            df["floor"] == df["total_floors"]
        ).astype(int)

    return df


def add_building_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "is_new_building" not in df.columns and "year_built" in df.columns:
        df["is_new_building"] = (df["year_built"] >= 2020).astype(int)

    if "is_high_floor" not in df.columns:
        df["is_high_floor"] = (df["floor"] >= 15).astype(int)

    if "is_low_rise" not in df.columns:
        df["is_low_rise"] = (df["total_floors"] <= 5).astype(int)

    if "is_large_apartment" not in df.columns:
        df["is_large_apartment"] = (df["area"] >= 100).astype(int)

    return df


def add_description_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "description_len" not in df.columns:
        if "description" not in df.columns:
            df["description"] = ""

        df["description"] = df["description"].fillna("").astype(str)
        df["description_len"] = df["description"].str.len()

    return df


def add_coordinate_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "lat" not in df.columns:
        df["lat"] = None

    if "lon" not in df.columns:
        df["lon"] = None

    if "coordinates_found" not in df.columns:
        df["coordinates_found"] = df["lat"].notna().astype(int)

    df["lat"] = df["lat"].fillna(
        df.groupby(["city", "district"])["lat"].transform("median")
    )

    df["lon"] = df["lon"].fillna(
        df.groupby(["city", "district"])["lon"].transform("median")
    )

    df["lat"] = df["lat"].fillna(
        df.groupby("city")["lat"].transform("median")
    )

    df["lon"] = df["lon"].fillna(
        df.groupby("city")["lon"].transform("median")
    )

    return df


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = add_house_age(df)
    df = add_floor_features(df)
    df = add_building_flags(df)
    df = add_description_features(df)
    df = add_coordinate_features(df)

    return df