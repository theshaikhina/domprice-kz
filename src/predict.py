import json
from functools import lru_cache

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor

from typing import Optional, List

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

    mape = 11.2

    min_price = pred_price * (1 - mape / 100)
    max_price = pred_price * (1 + mape / 100)

    return {
        "price": round(float(pred_price), 2),
        "price_per_m2": round(float(pred_price_per_m2), 2),
        "min_price": round(float(min_price), 2),
        "max_price": round(float(max_price), 2),
        "mape": mape,
    }


def make_options(
    df: pd.DataFrame,
    value_column: str,
    label_column: str,
    unknown_label: str = "Другое",
) -> list[dict]:
    if label_column not in df.columns:
        label_column = value_column

    if value_column == label_column:
        subset = df[[value_column]].dropna().drop_duplicates()
        subset[value_column] = subset[value_column].astype(str)
        subset = subset.sort_values(value_column)

        options = []

        for value in subset[value_column]:
            label = unknown_label if value == "unknown" else value

            options.append({
                "label": label,
                "value": value,
            })

        return options

    subset = df[[value_column, label_column]].dropna().drop_duplicates()

    subset[value_column] = subset[value_column].astype(str)
    subset[label_column] = subset[label_column].astype(str)

    subset = subset.sort_values(label_column)

    options = []

    for _, row in subset.iterrows():
        value = row[value_column]
        label = row[label_column]

        if value == "unknown":
            label = unknown_label

        options.append({
            "label": label,
            "value": value,
        })

    return options


def get_unique_values(
    value_column: str,
    label_column: Optional[str] = None,
    unknown_label: str = "Другое",
) -> list[dict]:
    df = load_reference_data()

    if label_column is None:
        label_column = value_column

    return make_options(
        df=df,
        value_column=value_column,
        label_column=label_column,
        unknown_label=unknown_label,
    )


def get_districts_by_city(
    city: str,
    value_column: str = "district",
    label_column: str = "district",
) -> list[dict]:
    df = load_reference_data()

    subset = df[df["city"] == city]

    return make_options(
        df=subset,
        value_column=value_column,
        label_column=label_column,
        unknown_label="Другой район",
    )


def get_residential_complexes(
    city: str,
    district: Optional[str] = None,
    value_column: str = "residential_complex",
    label_column: str = "residential_complex",
) -> List[dict]:
    df = load_reference_data()

    district = convert_display_value(district) if district else None

    subset = df[df["city"] == city]

    if district is not None:
        subset = subset[subset["district"] == district]

    return make_options(
        df=subset,
        value_column=value_column,
        label_column=label_column,
        unknown_label="Другой ЖК",
    )