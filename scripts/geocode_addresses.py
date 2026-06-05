import pandas as pd

from src.config import RAW_DATA_PATH, DATA_DIR
from src.geocoding import (
    build_geocode_query,
    get_unique_queries,
    geocode_queries,
    merge_coordinates,
)


if __name__ == "__main__":
    df = pd.read_csv(RAW_DATA_PATH)

    df = build_geocode_query(df)

    queries = get_unique_queries(df)

    output_path = DATA_DIR / "external" / "geocoded_addresses.csv"

    coords_df = geocode_queries(
        queries=queries,
        output_path=output_path,
        min_delay_seconds=1,
        save_every=50,
    )

    df_geo = merge_coordinates(df, coords_df)

    df_geo.to_csv(
        DATA_DIR / "processed" / "krisha_ads_with_coords.csv",
        index=False,
        encoding="utf-8-sig",
    )