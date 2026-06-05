import json
import numpy as np
import pandas as pd

from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split

from src.config import (
    RAW_DATA_PATH,
    PROCESSED_DATA_PATH,
    MODEL_PATH,
    FEATURES_PATH,
    CAT_FEATURES_PATH,
    REPORTS_DIR,
    FEATURES,
    CAT_FEATURES,
    TARGET,
    CATBOOST_PARAMS,
    TEST_SIZE,
    RANDOM_STATE,
)

from src.feature_engineering import create_features
from src.preprocessing import preprocess_data
from src.evaluate import calculate_metrics


def train_model():
    df = pd.read_csv(RAW_DATA_PATH)

    df = create_features(df)

    df = preprocess_data(
        df=df,
        features=FEATURES,
        cat_features=CAT_FEATURES,
    )

    df.to_csv(
        PROCESSED_DATA_PATH,
        index=False,
        encoding="utf-8-sig"
    )

    X = df[FEATURES]
    y = np.log1p(df[TARGET])

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    model = CatBoostRegressor(**CATBOOST_PARAMS)

    model.fit(
        X_train,
        y_train,
        cat_features=CAT_FEATURES,
        eval_set=(X_test, y_test),
    )

    preds = model.predict(X_test)

    metrics = calculate_metrics(
        y_true=y_test,
        y_pred=preds,
        log_target=True,
    )

    metrics = {
        metric_name: float(metric_value)
        for metric_name, metric_value in metrics.items()
    }

    print("Metrics:")
    for metric_name, metric_value in metrics.items():
        print(f"{metric_name}: {metric_value:.4f}")

    model.save_model(MODEL_PATH)

    with open(FEATURES_PATH, "w", encoding="utf-8") as f:
        json.dump(FEATURES, f, ensure_ascii=False, indent=2)

    with open(CAT_FEATURES_PATH, "w", encoding="utf-8") as f:
        json.dump(CAT_FEATURES, f, ensure_ascii=False, indent=2)

    feature_importance = pd.DataFrame({
        "feature": FEATURES,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False)

    feature_importance.to_csv(
        REPORTS_DIR / "feature_importance.csv",
        index=False,
        encoding="utf-8-sig",
    )

    with open(REPORTS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    return model, metrics


if __name__ == "__main__":
    train_model()