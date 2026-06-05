import time
import pandas as pd

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


def build_geocode_query(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["geocode_query"] = (
        df["city"].fillna("").astype(str)
        + ", "
        + df["address_clean"].fillna("").astype(str)
    )

    df["geocode_query"] = df["geocode_query"].str.strip()

    return df


def get_unique_queries(df: pd.DataFrame) -> pd.DataFrame:
    queries = (
        df[["geocode_query"]]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True)
    )

    queries = queries[
        queries["geocode_query"].str.len() > 3
    ]

    return queries


def geocode_query(query: str, geocode_func) -> dict:
    try:
        location = geocode_func(query)

        if location is None:
            return {
                "geocode_query": query,
                "lat": None,
                "lon": None,
                "geocode_address": None,
            }

        return {
            "geocode_query": query,
            "lat": location.latitude,
            "lon": location.longitude,
            "geocode_address": location.address,
        }

    except Exception:
        return {
            "geocode_query": query,
            "lat": None,
            "lon": None,
            "geocode_address": None,
        }


def geocode_queries(
    queries: pd.DataFrame,
    output_path: str,
    user_agent: str = "krisha_price_prediction",
    min_delay_seconds: int = 1,
    save_every: int = 50,
) -> pd.DataFrame:
    geolocator = Nominatim(user_agent=user_agent)

    geocode_func = RateLimiter(
        geolocator.geocode,
        min_delay_seconds=min_delay_seconds
    )

    results = []

    for i, query in enumerate(queries["geocode_query"], start=1):
        print(f"{i}/{len(queries)}: {query}")

        result = geocode_query(query, geocode_func)
        results.append(result)

        if i % save_every == 0:
            pd.DataFrame(results).to_csv(
                output_path,
                index=False,
                encoding="utf-8-sig"
            )

        time.sleep(0.1)

    coords_df = pd.DataFrame(results)

    coords_df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    return coords_df


def merge_coordinates(
    df: pd.DataFrame,
    coords_df: pd.DataFrame
) -> pd.DataFrame:
    df = df.copy()

    df = df.merge(
        coords_df,
        on="geocode_query",
        how="left"
    )

    return df