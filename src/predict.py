import json
from functools import lru_cache

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor

from typing import Optional

from src.config import (
    MODEL_PATH,
    FEATURES_PATH,
    PROCESSED_DATA_PATH,
)


CURRENT_YEAR = 2026

DISPLAY_TO_MODEL_VALUE = {
    "Другой": "unknown",
    "Другое": "unknown",
    "Другой район": "unknown",
}


@lru_cache(maxsize=1)
def load_features() -> list[str]:
    with open(FEATURES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_model() -> CatBoostRegressor:
    model = CatBoostRegressor()
    model.load_model(MODEL_PATH)
    return model


@lru_cache(maxsize=1)
def load_reference_data() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DATA_PATH)


def convert_display_value(value: str) -> str:
    return DISPLAY_TO_MODEL_VALUE.get(value, value)


def convert_input_values(data: dict) -> dict:
    data = data.copy()

    for col in [
        "city",
        "district",
        "residential_complex",
        "house_type",
        "condition",
        "bathroom",
    ]:
        data[col] = convert_display_value(data[col])

    return data


def get_location_fallback(
    df: pd.DataFrame,
    city: str,
    district: str,
    residential_complex: str,
) -> dict:
    subset = df[
        (df["city"] == city)
        & (df["district"] == district)
        & (df["residential_complex"] == residential_complex)
    ]

    if subset.empty:
        subset = df[
            (df["city"] == city)
            & (df["district"] == district)
        ]

    if subset.empty:
        subset = df[df["city"] == city]

    if subset.empty:
        subset = df

    return {
        "lat": subset["lat"].median(),
        "lon": subset["lon"].median(),
    }


def prepare_input(data: dict, features: list[str]) -> pd.DataFrame:
    data = convert_input_values(data)

    reference_df = load_reference_data()

    location_fallback = get_location_fallback(
        df=reference_df,
        city=data["city"],
        district=data["district"],
        residential_complex=data["residential_complex"],
    )

    data["lat"] = location_fallback["lat"]
    data["lon"] = location_fallback["lon"]
    data["coordinates_found"] = 0

    data["house_age"] = CURRENT_YEAR - data["year_built"]

    data["floor_ratio"] = data["floor"] / data["total_floors"]
    data["is_first_floor"] = int(data["floor"] == 1)
    data["is_last_floor"] = int(data["floor"] == data["total_floors"])

    data["description_len"] = 0

    input_df = pd.DataFrame([data])

    for feature in features:
        if feature not in input_df.columns:
            input_df[feature] = None

    input_df = input_df[features]

    return input_df


def predict_price(data: dict) -> dict:
    model = load_model()
    features = load_features()

    input_df = prepare_input(data, features)

    pred_log = model.predict(input_df)[0]

    pred_price_per_m2 = np.expm1(pred_log)
    pred_price = pred_price_per_m2 * data["area"]

    return {
        "predicted_price_per_m2": round(float(pred_price_per_m2), 2),
        "predicted_price": round(float(pred_price), 2),
    }


def get_unique_values(column: str) -> list[str]:
    df = load_reference_data()

    values = (
        df[column]
        .dropna()
        .astype(str)
        .sort_values()
        .unique()
        .tolist()
    )

    return replace_unknown_for_display(values)


def get_districts_by_city(city: str) -> list[str]:
    df = load_reference_data()

    values = (
        df[df["city"] == city]["district"]
        .dropna()
        .astype(str)
        .sort_values()
        .unique()
        .tolist()
    )

    return replace_unknown_for_display(values, unknown_value="Другой район")


def get_residential_complexes(
    city: str,
    district: Optional[str] = None,
) -> list[str]:
    df = load_reference_data()

    district = convert_display_value(district) if district else None

    subset = df[df["city"] == city]

    if district is not None:
        subset = subset[subset["district"] == district]

    values = (
        subset["residential_complex"]
        .dropna()
        .astype(str)
        .sort_values()
        .unique()
        .tolist()
    )

    return replace_unknown_for_display(values, unknown_value="Другой")


def replace_unknown_for_display(
    values: list[str],
    unknown_value: str = "Другое",
) -> list[str]:
    result = []

    for value in values:
        if value == "unknown":
            result.append(unknown_value)
        else:
            result.append(value)

    return result