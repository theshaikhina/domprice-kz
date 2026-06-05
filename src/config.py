from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

MODELS_DIR = PROJECT_DIR / "models"
REPORTS_DIR = PROJECT_DIR / "reports"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

RAW_DATA_PATH = RAW_DATA_DIR / "df_geo.csv"
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "krisha_ads_processed.csv"

MODEL_PATH = MODELS_DIR / "catboost_price_per_m2.cbm"
FEATURES_PATH = MODELS_DIR / "features.json"
CAT_FEATURES_PATH = MODELS_DIR / "cat_features.json"

TARGET = "price_per_m2"

FEATURES = [
    "rooms",
    "area",
    "floor",
    "total_floors",

    "city",
    "district",
    "residential_complex",

    "house_type",
    "condition",
    "bathroom",

    "ceiling_height",

    "house_age",
    "floor_ratio",
    "is_first_floor",
    "is_last_floor",
    "description_len",

    "lat",
    "lon",
    "coordinates_found",
    
    "is_new_building",
    "is_high_floor",
    "is_low_rise",
    "is_large_apartment"
]

CAT_FEATURES = [
    "city",
    "district",
    "residential_complex",
    "house_type",
    "condition",
    "bathroom",
]

CATBOOST_PARAMS = {
    "iterations": 1000,
    "learning_rate": 0.05,
    "depth": 8,
    "loss_function": "RMSE",
    "eval_metric": "RMSE",
    "random_seed": 42,
    "verbose": 100,
}

TEST_SIZE = 0.3
RANDOM_STATE = 42